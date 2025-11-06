"""
Service for initializing database and storage systems
"""

import asyncio
from typing import Dict, Any
from app.core.database import init_database, check_database_connection, get_database_info
from app.core.cloud_storage import storage_service, storage_config
from app.core.database_config import db_config, DatabaseType

class InitializationService:
    """Service to initialize all backend systems"""
    
    def __init__(self):
        self.initialization_status = {
            "database": False,
            "storage": False,
            "cache": False,
            "ai_services": False
        }
    
    async def initialize_all(self) -> Dict[str, Any]:
        """Initialize all systems and return status"""
        print("🚀 Initializing EduVerse Backend Systems...")
        
        # Initialize database
        await self._initialize_database()
        
        # Initialize storage
        await self._initialize_storage()
        
        # Initialize cache (Redis)
        await self._initialize_cache()
        
        # Initialize AI services
        await self._initialize_ai_services()
        
        return self.get_status()
    
    async def _initialize_database(self):
        """Initialize database system"""
        try:
            print(f"🗄️  Initializing {db_config.DB_TYPE.value} database...")
            
            # Check connection first
            if await check_database_connection():
                print("✅ Database connection successful")
                
                # Initialize tables
                await init_database()
                
                self.initialization_status["database"] = True
                
                # Print database info
                db_info = get_database_info()
                print(f"📊 Database Info: {db_info['type']} | Pool: {db_info['pool_size']} | SSL: {db_info['ssl_enabled']}")
                
            else:
                print("❌ Database connection failed")
                
        except Exception as e:
            print(f"❌ Database initialization failed: {e}")
    
    async def _initialize_storage(self):
        """Initialize cloud storage system"""
        global storage_service

        try:
            print(f"☁️  Initializing {storage_config.STORAGE_PROVIDER.value} storage...")

            # Test storage by uploading a small test file
            test_content = b"EduVerse storage test"
            test_path = "system/test.txt"

            url = await storage_service.upload_file(test_path, test_content, "text/plain")
            print(f"✅ Storage test successful: {url}")

            # Clean up test file
            await storage_service.delete_file(test_path)

            self.initialization_status["storage"] = True

            print(f"📁 Storage Info: {storage_config.STORAGE_PROVIDER.value} | CDN: {storage_config.CDN_ENABLED}")

        except Exception as e:
            print(f"❌ Storage initialization failed: {e}")
            # Fall back to local storage if cloud storage fails
            if storage_config.STORAGE_PROVIDER != "local":
                print("🔄 Falling back to local storage...")
                storage_config.STORAGE_PROVIDER = "local"
                # Retry with local storage
                try:
                    from app.core.cloud_storage import LocalStorageService
                    storage_service = LocalStorageService(storage_config)
                    await self._initialize_storage()
                except Exception as fallback_error:
                    print(f"❌ Local storage fallback failed: {fallback_error}")
    
    async def _initialize_cache(self):
        """Initialize Redis cache"""
        try:
            print("🔄 Initializing Redis cache...")
            
            # Test Redis connection
            import redis.asyncio as redis
            
            redis_client = redis.from_url("redis://localhost:6379")
            await redis_client.ping()
            await redis_client.close()
            
            print("✅ Redis cache initialized")
            self.initialization_status["cache"] = True
            
        except Exception as e:
            print(f"⚠️  Redis cache not available: {e}")
            print("💡 Continuing without cache (will use in-memory fallback)")
    
    async def _initialize_ai_services(self):
        """Initialize AI services"""
        try:
            print("🤖 Initializing AI services...")
            
            # Check if OpenAI API key is configured
            import os
            if os.getenv("OPENAI_API_KEY"):
                print("✅ OpenAI API configured")
                self.initialization_status["ai_services"] = True
            else:
                print("⚠️  OpenAI API key not configured")
                print("💡 AI features will be limited")
            
        except Exception as e:
            print(f"⚠️  AI services initialization warning: {e}")
    
    def get_status(self) -> Dict[str, Any]:
        """Get initialization status"""
        return {
            "status": "initialized" if all(self.initialization_status.values()) else "partial",
            "systems": self.initialization_status,
            "database": {
                "type": db_config.DB_TYPE.value,
                "status": "connected" if self.initialization_status["database"] else "failed"
            },
            "storage": {
                "provider": storage_config.STORAGE_PROVIDER.value,
                "status": "connected" if self.initialization_status["storage"] else "failed"
            },
            "features": {
                "cache": self.initialization_status["cache"],
                "ai_services": self.initialization_status["ai_services"],
                "real_time": True,  # WebSockets always available
                "file_upload": self.initialization_status["storage"]
            }
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Perform health check on all systems"""
        health_status = {}
        
        # Database health
        try:
            db_healthy = await check_database_connection()
            health_status["database"] = "healthy" if db_healthy else "unhealthy"
        except Exception:
            health_status["database"] = "unhealthy"
        
        # Storage health
        try:
            # Test storage with a small operation
            test_files = await storage_service.list_files("system/")
            health_status["storage"] = "healthy"
        except Exception:
            health_status["storage"] = "unhealthy"
        
        # Cache health
        try:
            import redis.asyncio as redis
            redis_client = redis.from_url("redis://localhost:6379")
            await redis_client.ping()
            await redis_client.close()
            health_status["cache"] = "healthy"
        except Exception:
            health_status["cache"] = "unhealthy"
        
        return {
            "overall": "healthy" if all(status == "healthy" for status in health_status.values()) else "degraded",
            "systems": health_status,
            "timestamp": "2024-01-15T10:30:00Z"
        }

# Global initialization service
init_service = InitializationService()

# Startup function
async def startup_initialization():
    """Function to call during app startup"""
    return await init_service.initialize_all()

# Health check function
async def system_health_check():
    """Function for health check endpoints"""
    return await init_service.health_check()
