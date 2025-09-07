"""
Global CDN and Content Delivery Service for worldwide low-latency access
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum
import json
import hashlib
import aiohttp
import aiofiles
import boto3
from botocore.exceptions import ClientError
import cloudflare
from azure.storage.blob.aio import BlobServiceClient
from google.cloud import storage as gcs
import redis.asyncio as redis
from PIL import Image
import io
import base64
import mimetypes
import asyncpg

logger = logging.getLogger(__name__)


class CDNProvider(str, Enum):
    CLOUDFLARE = "cloudflare"
    AWS_CLOUDFRONT = "aws_cloudfront"
    AZURE_CDN = "azure_cdn"
    GOOGLE_CDN = "google_cdn"
    FASTLY = "fastly"


class ContentType(str, Enum):
    VIDEO = "video"
    AUDIO = "audio"
    IMAGE = "image"
    DOCUMENT = "document"
    VR_CONTENT = "vr_content"
    AR_CONTENT = "ar_content"
    INTERACTIVE = "interactive"
    STREAMING = "streaming"


class CompressionType(str, Enum):
    GZIP = "gzip"
    BROTLI = "brotli"
    WEBP = "webp"
    AVIF = "avif"
    H264 = "h264"
    H265 = "h265"
    AV1 = "av1"


@dataclass
class CDNEndpoint:
    provider: CDNProvider
    region: str
    endpoint_url: str
    priority: int
    latency_ms: float
    bandwidth_mbps: float
    is_active: bool


@dataclass
class ContentItem:
    content_id: str
    content_type: ContentType
    original_url: str
    cdn_urls: Dict[str, str]  # region -> url mapping
    file_size_bytes: int
    mime_type: str
    compression_type: Optional[CompressionType]
    cache_duration_seconds: int
    created_at: datetime
    last_accessed: datetime
    access_count: int


class GlobalCDNService:
    """Advanced global CDN service with intelligent routing and optimization"""
    
    def __init__(self):
        self.cdn_providers = {}
        self.regional_endpoints = {}
        self.cache_client = None
        self.storage_clients = {}
        self.content_registry = {}
        
        # Performance monitoring
        self.latency_monitor = {}
        self.bandwidth_monitor = {}
        self.error_rates = {}
        
        # Content optimization
        self.image_optimizer = None
        self.video_optimizer = None
        self.compression_engines = {}
        
    async def initialize(self):
        """Initialize CDN service with multiple providers"""
        try:
            logger.info("Initializing Global CDN Service...")
            
            # Initialize cache client
            self.cache_client = redis.Redis(
                host='localhost',
                port=6379,
                decode_responses=True
            )
            
            # Initialize CDN providers
            await self._initialize_cdn_providers()
            
            # Initialize storage clients
            await self._initialize_storage_clients()
            
            # Initialize regional endpoints
            await self._discover_regional_endpoints()
            
            # Initialize content optimization
            await self._initialize_optimization_engines()
            
            # Start monitoring tasks
            asyncio.create_task(self._monitor_cdn_performance())
            asyncio.create_task(self._optimize_content_delivery())
            
            logger.info("Global CDN Service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize CDN service: {e}")
            raise
    
    async def upload_content(
        self,
        content_data: bytes,
        content_type: ContentType,
        filename: str,
        metadata: Dict[str, Any] = None
    ) -> ContentItem:
        """Upload content to global CDN with optimization"""
        
        content_id = hashlib.sha256(content_data).hexdigest()
        mime_type = mimetypes.guess_type(filename)[0] or 'application/octet-stream'
        
        try:
            # Optimize content based on type
            optimized_content = await self._optimize_content(
                content_data, content_type, mime_type
            )
            
            # Upload to multiple regions
            cdn_urls = {}
            upload_tasks = []
            
            for region, endpoint in self.regional_endpoints.items():
                task = self._upload_to_region(
                    optimized_content, content_id, filename, region, endpoint
                )
                upload_tasks.append(task)
            
            # Wait for all uploads to complete
            upload_results = await asyncio.gather(*upload_tasks, return_exceptions=True)
            
            # Process upload results
            for i, result in enumerate(upload_results):
                region = list(self.regional_endpoints.keys())[i]
                if not isinstance(result, Exception):
                    cdn_urls[region] = result
                else:
                    logger.error(f"Failed to upload to {region}: {result}")
            
            # Create content item
            content_item = ContentItem(
                content_id=content_id,
                content_type=content_type,
                original_url=cdn_urls.get('us-east-1', ''),
                cdn_urls=cdn_urls,
                file_size_bytes=len(optimized_content),
                mime_type=mime_type,
                compression_type=self._get_compression_type(mime_type),
                cache_duration_seconds=self._get_cache_duration(content_type),
                created_at=datetime.now(),
                last_accessed=datetime.now(),
                access_count=0
            )
            
            # Store in registry
            self.content_registry[content_id] = content_item
            
            # Cache content metadata
            await self._cache_content_metadata(content_item)
            
            return content_item
            
        except Exception as e:
            logger.error(f"Failed to upload content: {e}")
            raise
    
    async def get_optimal_url(
        self,
        content_id: str,
        user_location: Dict[str, Any],
        device_info: Dict[str, Any] = None
    ) -> str:
        """Get optimal CDN URL based on user location and device"""
        
        try:
            # Get content item
            content_item = await self._get_content_item(content_id)
            if not content_item:
                raise ValueError(f"Content {content_id} not found")
            
            # Determine optimal region
            optimal_region = await self._determine_optimal_region(
                user_location, content_item.cdn_urls.keys()
            )
            
            # Get device-optimized URL if needed
            if device_info:
                optimized_url = await self._get_device_optimized_url(
                    content_item, optimal_region, device_info
                )
                if optimized_url:
                    return optimized_url
            
            # Return standard optimal URL
            optimal_url = content_item.cdn_urls.get(optimal_region)
            if not optimal_url:
                # Fallback to any available URL
                optimal_url = next(iter(content_item.cdn_urls.values()))
            
            # Update access statistics
            await self._update_access_stats(content_id, optimal_region)
            
            return optimal_url
            
        except Exception as e:
            logger.error(f"Failed to get optimal URL: {e}")
            # Return fallback URL
            return await self._get_fallback_url(content_id)
    
    async def stream_content(
        self,
        content_id: str,
        user_location: Dict[str, Any],
        quality_preference: str = "auto"
    ) -> Dict[str, Any]:
        """Set up adaptive streaming for video/audio content"""
        
        try:
            content_item = await self._get_content_item(content_id)
            if not content_item:
                raise ValueError(f"Content {content_id} not found")
            
            if content_item.content_type not in [ContentType.VIDEO, ContentType.AUDIO]:
                raise ValueError("Streaming only available for video/audio content")
            
            # Generate adaptive streaming URLs
            streaming_urls = await self._generate_adaptive_streaming_urls(
                content_item, user_location, quality_preference
            )
            
            # Set up WebRTC for real-time streaming if needed
            webrtc_config = await self._setup_webrtc_streaming(
                content_item, user_location
            )
            
            return {
                'content_id': content_id,
                'streaming_urls': streaming_urls,
                'webrtc_config': webrtc_config,
                'adaptive_bitrates': await self._get_adaptive_bitrates(content_item),
                'subtitle_tracks': await self._get_subtitle_tracks(content_item),
                'thumbnail_urls': await self._get_thumbnail_urls(content_item)
            }
            
        except Exception as e:
            logger.error(f"Failed to set up streaming: {e}")
            raise
    
    async def optimize_for_region(
        self,
        content_id: str,
        target_regions: List[str],
        optimization_level: str = "balanced"
    ) -> Dict[str, Any]:
        """Optimize content delivery for specific regions"""
        
        try:
            content_item = await self._get_content_item(content_id)
            if not content_item:
                raise ValueError(f"Content {content_id} not found")
            
            optimization_results = {}
            
            for region in target_regions:
                # Analyze regional performance
                performance_data = await self._analyze_regional_performance(
                    content_id, region
                )
                
                # Apply region-specific optimizations
                optimizations = await self._apply_regional_optimizations(
                    content_item, region, optimization_level, performance_data
                )
                
                optimization_results[region] = {
                    'performance_data': performance_data,
                    'optimizations_applied': optimizations,
                    'expected_improvement': await self._calculate_expected_improvement(
                        performance_data, optimizations
                    )
                }
            
            return {
                'content_id': content_id,
                'optimization_results': optimization_results,
                'global_performance_impact': await self._calculate_global_impact(
                    optimization_results
                )
            }
            
        except Exception as e:
            logger.error(f"Failed to optimize for regions: {e}")
            raise
    
    async def setup_edge_caching(
        self,
        content_patterns: List[str],
        cache_policies: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Set up intelligent edge caching policies"""
        
        try:
            caching_config = {}
            
            for pattern in content_patterns:
                # Analyze content access patterns
                access_patterns = await self._analyze_access_patterns(pattern)
                
                # Determine optimal cache policy
                optimal_policy = await self._determine_cache_policy(
                    access_patterns, cache_policies
                )
                
                # Configure edge caching
                edge_config = await self._configure_edge_caching(
                    pattern, optimal_policy
                )
                
                caching_config[pattern] = {
                    'access_patterns': access_patterns,
                    'cache_policy': optimal_policy,
                    'edge_configuration': edge_config
                }
            
            # Apply configurations to CDN providers
            application_results = await self._apply_caching_configurations(
                caching_config
            )
            
            return {
                'caching_configurations': caching_config,
                'application_results': application_results,
                'estimated_performance_gain': await self._estimate_caching_benefits(
                    caching_config
                )
            }
            
        except Exception as e:
            logger.error(f"Failed to setup edge caching: {e}")
            raise
    
    async def monitor_global_performance(self) -> Dict[str, Any]:
        """Monitor global CDN performance and health"""
        
        try:
            performance_data = {}
            
            # Monitor each CDN provider
            for provider_name, provider in self.cdn_providers.items():
                provider_metrics = await self._monitor_provider_performance(
                    provider_name, provider
                )
                performance_data[provider_name] = provider_metrics
            
            # Monitor regional performance
            regional_metrics = {}
            for region, endpoint in self.regional_endpoints.items():
                region_metrics = await self._monitor_regional_performance(
                    region, endpoint
                )
                regional_metrics[region] = region_metrics
            
            # Analyze global trends
            global_trends = await self._analyze_global_trends(
                performance_data, regional_metrics
            )
            
            # Generate performance insights
            insights = await self._generate_performance_insights(
                performance_data, regional_metrics, global_trends
            )
            
            # Check for performance issues
            issues = await self._detect_performance_issues(
                performance_data, regional_metrics
            )
            
            return {
                'timestamp': datetime.now().isoformat(),
                'provider_performance': performance_data,
                'regional_performance': regional_metrics,
                'global_trends': global_trends,
                'insights': insights,
                'issues': issues,
                'recommendations': await self._generate_performance_recommendations(issues)
            }
            
        except Exception as e:
            logger.error(f"Failed to monitor performance: {e}")
            return {'error': str(e)}
    
    # Helper methods
    async def _initialize_cdn_providers(self):
        """Initialize CDN provider clients"""
        
        # Cloudflare
        try:
            self.cdn_providers[CDNProvider.CLOUDFLARE] = cloudflare.CloudFlare(
                email='your-email@example.com',
                token='your-cloudflare-token'
            )
        except Exception as e:
            logger.warning(f"Failed to initialize Cloudflare: {e}")
        
        # AWS CloudFront
        try:
            self.cdn_providers[CDNProvider.AWS_CLOUDFRONT] = boto3.client(
                'cloudfront',
                aws_access_key_id='your-access-key',
                aws_secret_access_key='your-secret-key'
            )
        except Exception as e:
            logger.warning(f"Failed to initialize AWS CloudFront: {e}")
        
        # Azure CDN
        try:
            # Initialize Azure CDN client (mock)
            logger.info("Azure CDN client initialization (mock)...")
        except Exception as e:
            logger.warning(f"Failed to initialize Azure CDN: {e}")
        
        # Google Cloud CDN
        try:
            self.cdn_providers[CDNProvider.GOOGLE_CDN] = gcs.Client()
        except Exception as e:
            logger.warning(f"Failed to initialize Google CDN: {e}")
    
    async def _initialize_storage_clients(self):
        """Initialize cloud storage clients"""
        
        # AWS S3
        try:
            self.storage_clients['s3'] = boto3.client(
                's3',
                aws_access_key_id='your-access-key',
                aws_secret_access_key='your-secret-key'
            )
        except Exception as e:
            logger.warning(f"Failed to initialize S3: {e}")
        
        # Azure Blob Storage
        try:
            self.storage_clients['azure'] = BlobServiceClient(
                account_url="https://youraccount.blob.core.windows.net",
                credential="your-account-key"
            )
        except Exception as e:
            logger.warning(f"Failed to initialize Azure Blob: {e}")
        
        # Google Cloud Storage
        try:
            self.storage_clients['gcs'] = gcs.Client()
        except Exception as e:
            logger.warning(f"Failed to initialize GCS: {e}")
    
    async def _discover_regional_endpoints(self):
        """Discover and configure regional CDN endpoints"""
        
        # Define major regions with their CDN endpoints
        regions = {
            'us-east-1': {
                'name': 'US East (N. Virginia)',
                'cloudflare': 'https://cdn-us-east.eduverse.com',
                'aws': 'https://d1234567890.cloudfront.net',
                'priority': 1
            },
            'us-west-1': {
                'name': 'US West (N. California)',
                'cloudflare': 'https://cdn-us-west.eduverse.com',
                'aws': 'https://d0987654321.cloudfront.net',
                'priority': 2
            },
            'eu-west-1': {
                'name': 'Europe (Ireland)',
                'cloudflare': 'https://cdn-eu-west.eduverse.com',
                'aws': 'https://d1122334455.cloudfront.net',
                'priority': 1
            },
            'ap-southeast-1': {
                'name': 'Asia Pacific (Singapore)',
                'cloudflare': 'https://cdn-ap-southeast.eduverse.com',
                'aws': 'https://d5544332211.cloudfront.net',
                'priority': 1
            },
            'ap-northeast-1': {
                'name': 'Asia Pacific (Tokyo)',
                'cloudflare': 'https://cdn-ap-northeast.eduverse.com',
                'aws': 'https://d9988776655.cloudfront.net',
                'priority': 2
            },
            'sa-east-1': {
                'name': 'South America (São Paulo)',
                'cloudflare': 'https://cdn-sa-east.eduverse.com',
                'aws': 'https://d6677889900.cloudfront.net',
                'priority': 3
            },
            'af-south-1': {
                'name': 'Africa (Cape Town)',
                'cloudflare': 'https://cdn-af-south.eduverse.com',
                'aws': 'https://d1357924680.cloudfront.net',
                'priority': 3
            }
        }
        
        for region_id, region_config in regions.items():
            endpoint = CDNEndpoint(
                provider=CDNProvider.CLOUDFLARE,  # Primary provider
                region=region_id,
                endpoint_url=region_config['cloudflare'],
                priority=region_config['priority'],
                latency_ms=0.0,  # Will be measured
                bandwidth_mbps=0.0,  # Will be measured
                is_active=True
            )
            
            self.regional_endpoints[region_id] = endpoint
            
            # Optionally test endpoint connectivity here if needed
            await self._test_endpoint_connectivity(endpoint)
    
    async def _optimize_content(
        self,
        content_data: bytes,
        content_type: ContentType,
        mime_type: str
    ) -> bytes:
        """Optimize content based on type and target delivery"""
        
        try:
            if content_type == ContentType.IMAGE:
                return await self._optimize_image(content_data, mime_type)
            elif content_type == ContentType.VIDEO:
                return await self._optimize_video(content_data, mime_type)
            elif content_type == ContentType.AUDIO:
                return await self._optimize_audio(content_data, mime_type)
            elif content_type == ContentType.DOCUMENT:
                return await self._optimize_document(content_data, mime_type)
            else:
                # Apply general compression
                return await self._apply_general_compression(content_data, mime_type)
                
        except Exception as e:
            logger.error(f"Failed to optimize content: {e}")
            return content_data  # Return original if optimization fails
    
    async def _optimize_image(self, image_data: bytes, mime_type: str) -> bytes:
        """Optimize image with multiple format support"""
        
        try:
            # Load image
            image = Image.open(io.BytesIO(image_data))
            
            # Convert to RGB if necessary
            if image.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', image.size, (255, 255, 255))
                if image.mode == 'P':
                    image = image.convert('RGBA')
                background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                image = background
            
            # Optimize based on content
            if image.width > 1920 or image.height > 1080:
                # Resize large images
                image.thumbnail((1920, 1080), Image.Resampling.LANCZOS)
            
            # Save with optimization
            output = io.BytesIO()
            
            # Choose optimal format
            if mime_type in ['image/jpeg', 'image/jpg']:
                image.save(output, format='JPEG', quality=85, optimize=True)
            elif mime_type == 'image/png':
                image.save(output, format='PNG', optimize=True)
            elif mime_type == 'image/webp':
                image.save(output, format='WEBP', quality=85, optimize=True)
            else:
                # Default to JPEG
                image.save(output, format='JPEG', quality=85, optimize=True)
            
            return output.getvalue()
            
        except Exception as e:
            logger.error(f"Failed to optimize image: {e}")
            return image_data
    
    async def _determine_optimal_region(
        self,
        user_location: Dict[str, Any],
        available_regions: List[str]
    ) -> str:
        """Determine optimal CDN region based on user location"""
        
        user_country = user_location.get('country', 'US')
        user_continent = user_location.get('continent', 'NA')
        
        # Region mapping based on geography
        region_mapping = {
            'US': 'us-east-1',
            'CA': 'us-east-1',
            'MX': 'us-east-1',
            'GB': 'eu-west-1',
            'DE': 'eu-west-1',
            'FR': 'eu-west-1',
            'IT': 'eu-west-1',
            'ES': 'eu-west-1',
            'JP': 'ap-northeast-1',
            'KR': 'ap-northeast-1',
            'CN': 'ap-northeast-1',
            'SG': 'ap-southeast-1',
            'IN': 'ap-southeast-1',
            'AU': 'ap-southeast-1',
            'BR': 'sa-east-1',
            'AR': 'sa-east-1',
            'ZA': 'af-south-1'
        }
        
        # Get preferred region
        preferred_region = region_mapping.get(user_country)
        
        # Check if preferred region is available
        if preferred_region and preferred_region in available_regions:
            return preferred_region
        
        # Fallback to continent-based selection
        continent_mapping = {
            'NA': 'us-east-1',  # North America
            'SA': 'sa-east-1',  # South America
            'EU': 'eu-west-1',  # Europe
            'AS': 'ap-southeast-1',  # Asia
            'AF': 'af-south-1',  # Africa
            'OC': 'ap-southeast-1'  # Oceania
        }
        
        continent_region = continent_mapping.get(user_continent, 'us-east-1')
        if continent_region in available_regions:
            return continent_region
        
        # Final fallback to first available region
        return available_regions[0] if available_regions else 'us-east-1'
    
    async def _monitor_cdn_performance(self):
        """Continuously monitor CDN performance"""
        
        while True:
            try:
                for region, endpoint in self.regional_endpoints.items():
                    # Measure latency
                    latency = await self._measure_endpoint_latency(endpoint)
                    endpoint.latency_ms = latency
                    
                    # Measure bandwidth
                    bandwidth = await self._measure_endpoint_bandwidth(endpoint)
                    endpoint.bandwidth_mbps = bandwidth
                    
                    # Update performance metrics
                    await self._update_performance_metrics(region, latency, bandwidth)
                
                # Sleep for monitoring interval
                await asyncio.sleep(60)  # Monitor every minute
                
            except Exception as e:
                logger.error(f"Error in CDN performance monitoring: {e}")
                await asyncio.sleep(60)
    
    async def cleanup(self):
        """Cleanup CDN service resources"""
        try:
            # Close cache client
            if self.cache_client:
                await self.cache_client.close()
            
            # Close storage clients
            for client in self.storage_clients.values():
                if hasattr(client, 'close'):
                    await client.close()
            
            logger.info("Global CDN Service cleaned up successfully")
            
        except Exception as e:
            logger.error(f"Error during CDN service cleanup: {e}")


# Global CDN service instance
cdn_service = None

async def get_cdn_service() -> GlobalCDNService:
    """Get CDN service instance"""
    global cdn_service
    if cdn_service is None:
        cdn_service = GlobalCDNService()
        await cdn_service.initialize()
    return cdn_service

async def close_cdn_service():
    """Close CDN service"""
    global cdn_service
    if cdn_service:
        await cdn_service.cleanup()
        cdn_service = None