"""
Database configuration with support for multiple database backends
"""

import os
from enum import Enum
from typing import Optional, Dict, Any
try:
    from pydantic_settings import BaseSettings
except ImportError:
    from pydantic import BaseSettings
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import StaticPool

class DatabaseType(str, Enum):
    SQLITE = "sqlite"
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    MONGODB = "mongodb"

class DatabaseConfig(BaseSettings):
    """Database configuration with environment variable support"""
    
    # Database type selection
    DB_TYPE: DatabaseType = DatabaseType.POSTGRESQL
    
    # PostgreSQL settings (default/recommended)
    POSTGRES_HOST: str = "localhost"
    POSTGRES_PORT: int = 5432
    POSTGRES_DB: str = "eduverse"
    POSTGRES_USER: str = "eduverse_user"
    POSTGRES_PASSWORD: str = "eduverse_password"
    
    # MySQL settings
    MYSQL_HOST: str = "localhost"
    MYSQL_PORT: int = 3306
    MYSQL_DB: str = "eduverse"
    MYSQL_USER: str = "eduverse_user"
    MYSQL_PASSWORD: str = "eduverse_password"
    
    # MongoDB settings
    MONGODB_HOST: str = "localhost"
    MONGODB_PORT: int = 27017
    MONGODB_DB: str = "eduverse"
    MONGODB_USER: Optional[str] = None
    MONGODB_PASSWORD: Optional[str] = None
    
    # SQLite settings (development/testing)
    SQLITE_PATH: str = "./database.db"
    
    # Cloud database URLs (override individual settings)
    DATABASE_URL: Optional[str] = None
    
    # Connection pool settings
    DB_POOL_SIZE: int = 20
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_TIMEOUT: int = 30
    DB_POOL_RECYCLE: int = 3600
    
    # SSL settings for cloud databases
    DB_SSL_MODE: str = "prefer"  # disable, allow, prefer, require
    DB_SSL_CERT: Optional[str] = None
    DB_SSL_KEY: Optional[str] = None
    DB_SSL_CA: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = True

    def get_database_url(self) -> str:
        """Get the appropriate database URL based on configuration"""
        
        # If explicit DATABASE_URL is provided, use it
        if self.DATABASE_URL:
            return self.DATABASE_URL
        
        # Build URL based on database type
        if self.DB_TYPE == DatabaseType.POSTGRESQL:
            return self._build_postgresql_url()
        elif self.DB_TYPE == DatabaseType.MYSQL:
            return self._build_mysql_url()
        elif self.DB_TYPE == DatabaseType.SQLITE:
            return self._build_sqlite_url()
        elif self.DB_TYPE == DatabaseType.MONGODB:
            return self._build_mongodb_url()
        else:
            raise ValueError(f"Unsupported database type: {self.DB_TYPE}")
    
    def get_async_database_url(self) -> str:
        """Get async database URL"""
        url = self.get_database_url()
        
        # Convert to async drivers
        if self.DB_TYPE == DatabaseType.POSTGRESQL:
            if "postgresql://" in url:
                return url.replace("postgresql://", "postgresql+asyncpg://")
            elif "postgresql+asyncpg://" not in url:
                return f"postgresql+asyncpg://{url}"
        elif self.DB_TYPE == DatabaseType.MYSQL:
            if "mysql://" in url:
                return url.replace("mysql://", "mysql+aiomysql://")
            elif "mysql+aiomysql://" not in url:
                return f"mysql+aiomysql://{url}"
        elif self.DB_TYPE == DatabaseType.SQLITE:
            if "sqlite://" in url:
                return url.replace("sqlite://", "sqlite+aiosqlite://")
            elif "sqlite+aiosqlite://" not in url:
                return f"sqlite+aiosqlite:///{url}"
        
        return url
    
    def _build_postgresql_url(self) -> str:
        """Build PostgreSQL connection URL"""
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )
    
    def _build_mysql_url(self) -> str:
        """Build MySQL connection URL"""
        return (
            f"mysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}"
            f"@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DB}"
        )
    
    def _build_sqlite_url(self) -> str:
        """Build SQLite connection URL"""
        return f"sqlite:///{self.SQLITE_PATH}"
    
    def _build_mongodb_url(self) -> str:
        """Build MongoDB connection URL"""
        if self.MONGODB_USER and self.MONGODB_PASSWORD:
            return (
                f"mongodb://{self.MONGODB_USER}:{self.MONGODB_PASSWORD}"
                f"@{self.MONGODB_HOST}:{self.MONGODB_PORT}/{self.MONGODB_DB}"
            )
        return f"mongodb://{self.MONGODB_HOST}:{self.MONGODB_PORT}/{self.MONGODB_DB}"
    
    def get_engine_kwargs(self) -> Dict[str, Any]:
        """Get engine-specific kwargs"""
        kwargs = {}
        
        # SQLite specific settings
        if self.DB_TYPE == DatabaseType.SQLITE:
            kwargs.update({
                "poolclass": StaticPool,
                "connect_args": {"check_same_thread": False}
            })
        else:
            # Pool settings for other databases
            kwargs.update({
                "pool_size": self.DB_POOL_SIZE,
                "max_overflow": self.DB_MAX_OVERFLOW,
                "pool_timeout": self.DB_POOL_TIMEOUT,
                "pool_recycle": self.DB_POOL_RECYCLE,
            })
        
        # SSL settings for cloud databases
        if self.DB_TYPE in [DatabaseType.POSTGRESQL, DatabaseType.MYSQL]:
            connect_args = kwargs.get("connect_args", {})
            
            if self.DB_SSL_MODE != "disable":
                connect_args["sslmode"] = self.DB_SSL_MODE
                
                if self.DB_SSL_CERT:
                    connect_args["sslcert"] = self.DB_SSL_CERT
                if self.DB_SSL_KEY:
                    connect_args["sslkey"] = self.DB_SSL_KEY
                if self.DB_SSL_CA:
                    connect_args["sslrootcert"] = self.DB_SSL_CA
            
            if connect_args:
                kwargs["connect_args"] = connect_args
        
        return kwargs

# Global database configuration
db_config = DatabaseConfig()

# Create Base for all models
Base = declarative_base()

# Create engines
engine = create_engine(
    db_config.get_database_url(),
    echo=os.getenv("DEBUG", "false").lower() == "true",
    **db_config.get_engine_kwargs()
)

async_engine = create_async_engine(
    db_config.get_async_database_url(),
    echo=os.getenv("DEBUG", "false").lower() == "true",
    **db_config.get_engine_kwargs()
)

# Create session factories
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
AsyncSessionLocal = sessionmaker(
    async_engine, class_=AsyncSession, expire_on_commit=False
)

async def get_db():
    """Dependency to get database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

async def create_tables():
    """Create all database tables"""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def drop_tables():
    """Drop all database tables"""
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

# Cloud database presets
CLOUD_DATABASE_PRESETS = {
    "aws_rds_postgres": {
        "DB_TYPE": "postgresql",
        "POSTGRES_HOST": "{RDS_ENDPOINT}",
        "POSTGRES_PORT": 5432,
        "DB_SSL_MODE": "require"
    },
    "gcp_cloud_sql_postgres": {
        "DB_TYPE": "postgresql", 
        "DATABASE_URL": "postgresql+asyncpg://{USER}:{PASSWORD}@/{DATABASE}?host=/cloudsql/{INSTANCE_CONNECTION_NAME}"
    },
    "azure_postgres": {
        "DB_TYPE": "postgresql",
        "POSTGRES_HOST": "{SERVER_NAME}.postgres.database.azure.com",
        "POSTGRES_PORT": 5432,
        "DB_SSL_MODE": "require"
    },
    "planetscale_mysql": {
        "DB_TYPE": "mysql",
        "DATABASE_URL": "mysql+aiomysql://{USERNAME}:{PASSWORD}@{HOST}/{DATABASE}?ssl_ca=/etc/ssl/certs/ca-certificates.crt&ssl_verify_cert=true"
    },
    "mongodb_atlas": {
        "DB_TYPE": "mongodb",
        "DATABASE_URL": "mongodb+srv://{USERNAME}:{PASSWORD}@{CLUSTER}.mongodb.net/{DATABASE}?retryWrites=true&w=majority"
    },
    "supabase_postgres": {
        "DB_TYPE": "postgresql",
        "DATABASE_URL": "postgresql+asyncpg://{USER}:{PASSWORD}@{HOST}:5432/{DATABASE}"
    },
    "neon_postgres": {
        "DB_TYPE": "postgresql", 
        "DATABASE_URL": "postgresql+asyncpg://{USER}:{PASSWORD}@{HOST}/{DATABASE}?sslmode=require"
    }
}