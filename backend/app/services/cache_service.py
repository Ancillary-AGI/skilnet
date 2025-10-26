"""
Advanced caching service with Redis and multiple strategies
"""

import json
import logging
import asyncio
from typing import Any, Dict, List, Optional, Union
from datetime import datetime, timedelta
import hashlib
import pickle
from dataclasses import dataclass
from enum import Enum
import redis.asyncio as redis

logger = logging.getLogger(__name__)


class CacheStrategy(str, Enum):
    """Cache eviction strategies"""
    LRU = "lru"  # Least Recently Used
    LFU = "lfu"  # Least Frequently Used
    TTL = "ttl"  # Time To Live
    WRITE_THROUGH = "write_through"
    WRITE_BACK = "write_back"


class CacheType(str, Enum):
    """Types of cache"""
    USER_DATA = "user_data"
    COURSE_DATA = "course_data"
    ANALYTICS = "analytics"
    SESSION = "session"
    API_RESPONSE = "api_response"
    FILE_METADATA = "file_metadata"


@dataclass
class CacheConfig:
    """Cache configuration"""
    max_memory: int = 100 * 1024 * 1024  # 100MB
    default_ttl: int = 3600  # 1 hour
    compression_threshold: int = 1024  # Compress items > 1KB
    enable_compression: bool = True
    strategy: CacheStrategy = CacheStrategy.LRU


@dataclass
class CacheItem:
    """Cache item with metadata"""
    key: str
    value: Any
    ttl: Optional[int]
    created_at: datetime
    last_accessed: datetime
    access_count: int
    size_bytes: int
    cache_type: CacheType


class CacheService:
    """Advanced caching service with Redis backend"""

    def __init__(self, redis_url: str = "redis://localhost:6379", config: Optional[CacheConfig] = None):
        self.redis_url = redis_url
        self.config = config or CacheConfig()
        self.redis_client: Optional[redis.Redis] = None
        self.cache_stats = {
            'hits': 0,
            'misses': 0,
            'sets': 0,
            'deletes': 0,
            'evictions': 0
        }
        self._local_cache = {}  # Simple local cache for frequently accessed items

    async def initialize(self):
        """Initialize Redis connection"""
        try:
            self.redis_client = redis.Redis.from_url(
                self.redis_url,
                decode_responses=False,  # Keep as bytes for better performance
                max_connections=20,
                retry_on_timeout=True
            )

            # Test connection
            await self.redis_client.ping()
            logger.info("Cache service initialized successfully")

            # Start background tasks
            asyncio.create_task(self._cleanup_expired_items())
            asyncio.create_task(self._monitor_cache_performance())

        except Exception as e:
            logger.error(f"Failed to initialize cache service: {e}")
            # Fallback to local cache only
            self.redis_client = None

    async def get(self, key: str, cache_type: CacheType = CacheType.USER_DATA) -> Optional[Any]:
        """Get item from cache"""
        try:
            # Check local cache first
            if key in self._local_cache:
                item = self._local_cache[key]
                item.last_accessed = datetime.now()
                item.access_count += 1
                self.cache_stats['hits'] += 1
                return item.value

            # Check Redis cache
            if self.redis_client:
                cache_key = self._make_cache_key(key, cache_type)
                data = await self.redis_client.get(cache_key)

                if data:
                    # Deserialize
                    item = await self._deserialize_item(data)
                    if item:
                        # Update access metadata
                        item.last_accessed = datetime.now()
                        item.access_count += 1

                        # Add to local cache if frequently accessed
                        if item.access_count > 5:
                            self._local_cache[key] = item

                        # Update Redis metadata
                        await self._update_metadata(cache_key, item)

                        self.cache_stats['hits'] += 1
                        return item.value

            self.cache_stats['misses'] += 1
            return None

        except Exception as e:
            logger.error(f"Cache get error for key {key}: {e}")
            self.cache_stats['misses'] += 1
            return None

    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        cache_type: CacheType = CacheType.USER_DATA
    ) -> bool:
        """Set item in cache"""
        try:
            ttl = ttl or self.config.default_ttl
            cache_key = self._make_cache_key(key, cache_type)

            # Create cache item
            item = CacheItem(
                key=key,
                value=value,
                ttl=ttl,
                created_at=datetime.now(),
                last_accessed=datetime.now(),
                access_count=1,
                size_bytes=self._calculate_size(value),
                cache_type=cache_type
            )

            # Serialize
            data = await self._serialize_item(item)

            # Store in Redis
            if self.redis_client:
                success = await self.redis_client.setex(cache_key, ttl, data)
                if success:
                    # Store metadata separately for analytics
                    await self._store_metadata(cache_key, item)
                    self.cache_stats['sets'] += 1

                    # Add to local cache
                    self._local_cache[key] = item
                    return True

            return False

        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}")
            return False

    async def delete(self, key: str, cache_type: CacheType = CacheType.USER_DATA) -> bool:
        """Delete item from cache"""
        try:
            cache_key = self._make_cache_key(key, cache_type)

            # Remove from local cache
            if key in self._local_cache:
                del self._local_cache[key]

            # Remove from Redis
            if self.redis_client:
                result = await self.redis_client.delete(cache_key)
                if result:
                    # Remove metadata
                    await self._delete_metadata(cache_key)
                    self.cache_stats['deletes'] += 1
                    return True

            return False

        except Exception as e:
            logger.error(f"Cache delete error for key {key}: {e}")
            return False

    async def exists(self, key: str, cache_type: CacheType = CacheType.USER_DATA) -> bool:
        """Check if key exists in cache"""
        try:
            cache_key = self._make_cache_key(key, cache_type)

            # Check local cache
            if key in self._local_cache:
                return True

            # Check Redis
            if self.redis_client:
                return await self.redis_client.exists(cache_key) > 0

            return False

        except Exception as e:
            logger.error(f"Cache exists error for key {key}: {e}")
            return False

    async def clear_cache_type(self, cache_type: CacheType) -> int:
        """Clear all items of a specific cache type"""
        try:
            pattern = f"{cache_type.value}:*"

            if self.redis_client:
                keys = await self.redis_client.keys(pattern)
                if keys:
                    deleted = await self.redis_client.delete(*keys)
                    self.cache_stats['deletes'] += deleted
                    return deleted

            return 0

        except Exception as e:
            logger.error(f"Cache clear error for type {cache_type}: {e}")
            return 0

    async def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics"""
        try:
            total_requests = self.cache_stats['hits'] + self.cache_stats['misses']
            hit_rate = (self.cache_stats['hits'] / total_requests) if total_requests > 0 else 0

            stats = {
                'hits': self.cache_stats['hits'],
                'misses': self.cache_stats['misses'],
                'sets': self.cache_stats['sets'],
                'deletes': self.cache_stats['deletes'],
                'evictions': self.cache_stats['evictions'],
                'hit_rate': hit_rate,
                'total_requests': total_requests,
                'local_cache_size': len(self._local_cache)
            }

            # Add Redis info if available
            if self.redis_client:
                redis_info = await self.redis_client.info()
                stats['redis_info'] = {
                    'used_memory': redis_info.get('used_memory'),
                    'connected_clients': redis_info.get('connected_clients'),
                    'total_connections_received': redis_info.get('total_connections_received')
                }

            return stats

        except Exception as e:
            logger.error(f"Error getting cache stats: {e}")
            return {}

    async def warmup_cache(self, items: Dict[str, Any], cache_type: CacheType = CacheType.USER_DATA):
        """Warm up cache with initial data"""
        try:
            for key, value in items.items():
                await self.set(key, value, cache_type=cache_type)

            logger.info(f"Cache warmed up with {len(items)} items")

        except Exception as e:
            logger.error(f"Cache warmup error: {e}")

    async def get_or_set(
        self,
        key: str,
        fetch_func,
        ttl: Optional[int] = None,
        cache_type: CacheType = CacheType.USER_DATA
    ) -> Any:
        """Get from cache or set if not exists"""
        try:
            # Try to get from cache
            cached_value = await self.get(key, cache_type)
            if cached_value is not None:
                return cached_value

            # Fetch from source
            value = await fetch_func()

            # Cache the result
            if value is not None:
                await self.set(key, value, ttl, cache_type)

            return value

        except Exception as e:
            logger.error(f"Get or set error for key {key}: {e}")
            # Fallback to fetch function
            return await fetch_func()

    # Helper methods
    def _make_cache_key(self, key: str, cache_type: CacheType) -> str:
        """Create a cache key with namespace"""
        return f"{cache_type.value}:{key}"

    def _calculate_size(self, value: Any) -> int:
        """Calculate size of value in bytes"""
        try:
            return len(pickle.dumps(value))
        except:
            return len(str(value).encode('utf-8'))

    async def _serialize_item(self, item: CacheItem) -> bytes:
        """Serialize cache item"""
        try:
            data = {
                'key': item.key,
                'value': item.value,
                'ttl': item.ttl,
                'created_at': item.created_at.isoformat(),
                'last_accessed': item.last_accessed.isoformat(),
                'access_count': item.access_count,
                'size_bytes': item.size_bytes,
                'cache_type': item.cache_type.value
            }

            json_data = json.dumps(data, default=str)
            return json_data.encode('utf-8')

        except Exception as e:
            logger.error(f"Serialization error: {e}")
            return b""

    async def _deserialize_item(self, data: bytes) -> Optional[CacheItem]:
        """Deserialize cache item"""
        try:
            json_data = json.loads(data.decode('utf-8'))

            return CacheItem(
                key=json_data['key'],
                value=json_data['value'],
                ttl=json_data['ttl'],
                created_at=datetime.fromisoformat(json_data['created_at']),
                last_accessed=datetime.fromisoformat(json_data['last_accessed']),
                access_count=json_data['access_count'],
                size_bytes=json_data['size_bytes'],
                cache_type=CacheType(json_data['cache_type'])
            )

        except Exception as e:
            logger.error(f"Deserialization error: {e}")
            return None

    async def _store_metadata(self, cache_key: str, item: CacheItem):
        """Store cache item metadata"""
        try:
            metadata_key = f"metadata:{cache_key}"
            metadata = {
                'last_accessed': item.last_accessed.isoformat(),
                'access_count': item.access_count,
                'size_bytes': item.size_bytes
            }

            await self.redis_client.setex(
                metadata_key,
                item.ttl or self.config.default_ttl,
                json.dumps(metadata).encode('utf-8')
            )

        except Exception as e:
            logger.error(f"Metadata store error: {e}")

    async def _update_metadata(self, cache_key: str, item: CacheItem):
        """Update cache item metadata"""
        try:
            metadata_key = f"metadata:{cache_key}"
            metadata = {
                'last_accessed': item.last_accessed.isoformat(),
                'access_count': item.access_count,
                'size_bytes': item.size_bytes
            }

            # Get current TTL
            current_ttl = await self.redis_client.ttl(cache_key)
            if current_ttl > 0:
                await self.redis_client.setex(
                    metadata_key,
                    current_ttl,
                    json.dumps(metadata).encode('utf-8')
                )

        except Exception as e:
            logger.error(f"Metadata update error: {e}")

    async def _delete_metadata(self, cache_key: str):
        """Delete cache item metadata"""
        try:
            metadata_key = f"metadata:{cache_key}"
            await self.redis_client.delete(metadata_key)

        except Exception as e:
            logger.error(f"Metadata delete error: {e}")

    async def _cleanup_expired_items(self):
        """Background task to cleanup expired items"""
        while True:
            try:
                # Cleanup local cache
                expired_keys = []
                for key, item in self._local_cache.items():
                    if item.ttl and (datetime.now() - item.created_at).seconds > item.ttl:
                        expired_keys.append(key)

                for key in expired_keys:
                    del self._local_cache[key]
                    self.cache_stats['evictions'] += 1

                # Redis cleanup is handled automatically by TTL
                await asyncio.sleep(300)  # Run every 5 minutes

            except Exception as e:
                logger.error(f"Cleanup error: {e}")
                await asyncio.sleep(300)

    async def _monitor_cache_performance(self):
        """Background task to monitor cache performance"""
        while True:
            try:
                # Log performance stats every 10 minutes
                stats = await self.get_cache_stats()
                logger.info(f"Cache performance: {stats}")

                await asyncio.sleep(600)  # Run every 10 minutes

            except Exception as e:
                logger.error(f"Performance monitoring error: {e}")
                await asyncio.sleep(600)

    async def close(self):
        """Close cache service"""
        try:
            if self.redis_client:
                await self.redis_client.close()
            self._local_cache.clear()
            logger.info("Cache service closed")

        except Exception as e:
            logger.error(f"Error closing cache service: {e}")


# Global cache service instance
cache_service = None

async def get_cache_service() -> CacheService:
    """Get cache service instance"""
    global cache_service
    if cache_service is None:
        cache_service = CacheService()
        await cache_service.initialize()
    return cache_service

async def close_cache_service():
    """Close cache service"""
    global cache_service
    if cache_service:
        await cache_service.close()
        cache_service = None
