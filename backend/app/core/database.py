"""
Database module with flexible backend support and cloud storage integration
"""

from sqlalchemy.ext.asyncio import AsyncSession
from typing import AsyncGenerator
from .database_config import (
    Base, async_engine, AsyncSessionLocal, get_db, create_tables, drop_tables,
    db_config, DatabaseType
)

# Re-export for backward compatibility
__all__ = [
    "Base", "async_engine", "AsyncSessionLocal", "get_db", 
    "create_tables", "drop_tables", "db_config", "DatabaseType"
]

# Database utilities
async def init_database():
    """Initialize database with tables"""
    print(f"🗄️  Initializing {db_config.DB_TYPE.value} database...")
    
    if db_config.DB_TYPE == DatabaseType.MONGODB:
        # MongoDB doesn't use SQLAlchemy tables
        print("📄 MongoDB initialized (no table creation needed)")
        return
    
    try:
        await create_tables()
        print("✅ Database tables created successfully")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        raise

async def check_database_connection():
    """Check if database connection is working"""
    try:
        async with AsyncSessionLocal() as session:
            if db_config.DB_TYPE == DatabaseType.SQLITE:
                await session.execute("SELECT 1")
            elif db_config.DB_TYPE == DatabaseType.POSTGRESQL:
                await session.execute("SELECT version()")
            elif db_config.DB_TYPE == DatabaseType.MYSQL:
                await session.execute("SELECT VERSION()")
            
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def get_database_info():
    """Get current database configuration info"""
    return {
        "type": db_config.DB_TYPE.value,
        "url": db_config.get_database_url().split("@")[-1] if "@" in db_config.get_database_url() else "local",
        "pool_size": db_config.DB_POOL_SIZE,
        "ssl_enabled": db_config.DB_SSL_MODE != "disable"
    }

# MongoDB support (if needed)
try:
    from motor.motor_asyncio import AsyncIOMotorClient
    from pymongo.errors import ConnectionFailure
    
    class MongoDatabase:
        def __init__(self):
            self.client = None
            self.database = None
        
        async def connect(self):
            """Connect to MongoDB"""
            if db_config.DB_TYPE == DatabaseType.MONGODB:
                self.client = AsyncIOMotorClient(db_config.get_database_url())
                self.database = self.client[db_config.MONGODB_DB]
                
                # Test connection
                await self.client.admin.command('ping')
                print("✅ MongoDB connected successfully")
        
        async def disconnect(self):
            """Disconnect from MongoDB"""
            if self.client:
                self.client.close()
        
        def get_collection(self, name: str):
            """Get MongoDB collection"""
            if self.database:
                return self.database[name]
            return None
    
    # Global MongoDB instance
    mongo_db = MongoDatabase()
    
except ImportError:
    # MongoDB dependencies not installed
    mongo_db = None
    print("💡 MongoDB support not available (install motor and pymongo)")

# Database migration utilities
class DatabaseMigration:
    """Handle database migrations across different backends"""
    
    @staticmethod
    async def migrate_to_postgres():
        """Migrate from SQLite to PostgreSQL"""
        print("🔄 Migrating to PostgreSQL...")
        # Implementation would depend on specific migration needs
        pass
    
    @staticmethod
    async def migrate_to_mysql():
        """Migrate from current DB to MySQL"""
        print("🔄 Migrating to MySQL...")
        # Implementation would depend on specific migration needs
        pass
    
    @staticmethod
    async def backup_database():
        """Create database backup"""
        print("💾 Creating database backup...")
        # Implementation would depend on database type
        pass
    
    @staticmethod
    async def restore_database(backup_path: str):
        """Restore database from backup"""
        print(f"📥 Restoring database from {backup_path}...")
        # Implementation would depend on database type
        pass