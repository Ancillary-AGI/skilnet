"""
Database module with flexible backend support and cloud storage integration
"""

from importlib import import_module
from importlib.util import find_spec
from typing import AsyncGenerator, Dict, Any, Optional, Union

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from .database_config import (
    Base, async_engine, AsyncSessionLocal, get_db, create_tables, drop_tables,
    db_config, DatabaseType
)


class Field:
    """Database field definition for custom ORM"""

    def __init__(
        self,
        field_type: str,
        primary_key: bool = False,
        nullable: bool = True,
        default: Any = None,
        index: bool = False,
        unique: bool = False,
        autoincrement: bool = False
    ):
        self.field_type = field_type.upper()
        self.primary_key = primary_key
        self.nullable = nullable
        self.default = default
        self.index = index
        self.unique = unique
        self.autoincrement = autoincrement

    def sql_definition(self, name: str, is_sqlite: bool = False) -> str:
        """Generate SQL column definition"""
        parts = [name]

        # Field type
        if self.field_type == 'INTEGER':
            parts.append('INTEGER')
        elif self.field_type == 'REAL':
            parts.append('REAL')
        elif self.field_type == 'TEXT':
            parts.append('TEXT')
        elif self.field_type == 'BOOLEAN':
            parts.append('BOOLEAN')
        elif self.field_type == 'TIMESTAMP':
            parts.append('TIMESTAMP')
        elif self.field_type == 'JSON':
            parts.append('TEXT')  # SQLite doesn't have JSON, use TEXT
        else:
            parts.append(self.field_type)

        # Primary key
        if self.primary_key:
            parts.append('PRIMARY KEY')

        # Autoincrement
        if self.autoincrement and self.field_type == 'INTEGER':
            if is_sqlite:
                parts.append('AUTOINCREMENT')
            else:
                parts.append('AUTO_INCREMENT')

        # Not null
        if not self.nullable:
            parts.append('NOT NULL')

        # Unique
        if self.unique:
            parts.append('UNIQUE')

        # Default
        if self.default is not None:
            if callable(self.default):
                # For functions like CURRENT_TIMESTAMP
                if self.default.__name__ == 'CURRENT_TIMESTAMP':
                    parts.append('DEFAULT CURRENT_TIMESTAMP')
            elif isinstance(self.default, str):
                parts.append(f"DEFAULT '{self.default}'")
            else:
                parts.append(f"DEFAULT {self.default}")

        return ' '.join(parts)


class DatabaseConnection:
    """Database connection manager singleton"""

    _instance = None
    _initialized = False

    def __init__(self, config):
        if DatabaseConnection._instance is not None:
            raise Exception("DatabaseConnection is a singleton class")

        self.config = config
        self._connection = None
        DatabaseConnection._instance = self

    @classmethod
    def get_instance(cls, config=None):
        """Get singleton instance"""
        if cls._instance is None:
            if config is None:
                raise Exception("DatabaseConnection not initialized")
            cls._instance = cls(config)
        return cls._instance

    async def get_connection(self):
        """Get database connection"""
        if self.config.DB_TYPE == DatabaseType.SQLITE:
            # For SQLite, return the session
            return AsyncSessionLocal()
        else:
            # For other databases, return the async session
            return AsyncSessionLocal()

    async def close(self):
        """Close database connection"""
        if self._connection:
            await self._connection.close()
            self._connection = None

# Re-export for backward compatibility
__all__ = [
    "Base", "async_engine", "AsyncSessionLocal", "get_db",
    "create_tables", "drop_tables", "db_config", "DatabaseType",
    "Field", "DatabaseConnection"
]

# Database utilities
async def init_database():
    """Initialize database with tables"""
    print(f"Initializing {db_config.DB_TYPE.value} database...")
    
    if db_config.DB_TYPE == DatabaseType.MONGODB:
        # MongoDB doesn't use SQLAlchemy tables
        print("📄 MongoDB initialized (no table creation needed)")
        return
    
    try:
        await create_tables()
        print("Database tables created successfully")
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        raise

async def check_database_connection():
    """Check if database connection is working"""
    try:
        async with AsyncSessionLocal() as session:
            # Use connection directly for raw SQL
            async with async_engine.connect() as conn:
                if db_config.DB_TYPE == DatabaseType.SQLITE:
                    await conn.execute(text("SELECT 1"))
                elif db_config.DB_TYPE == DatabaseType.POSTGRESQL:
                    await conn.execute(text("SELECT version()"))
                elif db_config.DB_TYPE == DatabaseType.MYSQL:
                    await conn.execute(text("SELECT VERSION()"))

        return True
    except Exception as e:
        print(f"Database connection failed: {e}")
        return False

def get_database_info():
    """Get current database configuration info"""
    return {
        "type": db_config.DB_TYPE.value,
        "url": db_config.get_database_url().split("@")[-1] if "@" in db_config.get_database_url() else "local",
        "pool_size": db_config.DB_POOL_SIZE,
        "ssl_enabled": db_config.DB_SSL_MODE != "disable"
    }

# MongoDB support (if needed) - imported conditionally
try:
    from motor.motor_asyncio import AsyncIOMotorClient
    from pymongo.errors import ConnectionFailure
    MONGODB_AVAILABLE = True
except ImportError:
    MONGODB_AVAILABLE = False
    AsyncIOMotorClient = None
    ConnectionFailure = None

class MongoDatabase:
    def __init__(self):
        self.client = None
        self.database = None
    
    async def connect(self):
        """Connect to MongoDB"""
        if db_config.DB_TYPE == DatabaseType.MONGODB:
            if not MONGODB_AVAILABLE:
                raise ImportError("MongoDB dependencies not installed. Install motor and pymongo.")
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