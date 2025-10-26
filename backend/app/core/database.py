from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from typing import AsyncGenerator
from contextlib import asynccontextmanager
from pydantic import BaseModel as PydanticBaseModel

# Create Base for all models
Base = declarative_base()

# Database URL - using SQLite for simplicity
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./database.db")

# Create async engine
engine = create_async_engine(
    DATABASE_URL.replace("sqlite://", "sqlite+aiosqlite://"),
    echo=True,  # Set to False in production
    future=True,
)

# Create session factory
async_session = sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to get database session"""
    async with async_session() as session:
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
    from app.models.user import User
    from app.models.course import Course
    from app.models.category import Category
    from app.models.profile import UserProfile
    from app.models.subscription import Subscription

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Database Configuration Classes
class DatabaseConfig:
    def __init__(self, database_url: str = None, is_sqlite: bool = True):
        self.database_url = database_url or DATABASE_URL
        self.is_sqlite = is_sqlite

class DatabaseConnection:
    _instances = {}

    @classmethod
    def get_instance(cls, config: DatabaseConfig):
        key = config.database_url
        if key not in cls._instances:
            cls._instances[key] = cls(config)
        return cls._instances[key]

    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.engine = create_async_engine(
            config.database_url.replace("sqlite://", "sqlite+aiosqlite://") if config.is_sqlite else config.database_url,
            echo=True,
            future=True,
        )

    @asynccontextmanager
    async def get_connection(self):
        async with self.engine.begin() as conn:
            yield conn

class Field:
    def __init__(self, field_type: str, primary_key: bool = False, nullable: bool = True,
                 default=None, index: bool = False, autoincrement: bool = False, unique: bool = False):
        self.field_type = field_type
        self.primary_key = primary_key
        self.nullable = nullable
        self.default = default
        self.index = index
        self.autoincrement = autoincrement
        self.unique = unique

    def sql_definition(self, name: str, is_sqlite: bool = True) -> str:
        """Generate SQL column definition"""
        sql = f"{name} {self.field_type}"

        if self.unique:
            sql += " UNIQUE"

        if self.primary_key:
            sql += " PRIMARY KEY"
            if is_sqlite and self.autoincrement:
                sql += " AUTOINCREMENT"

        if not self.nullable:
            sql += " NOT NULL"

        if self.default is not None:
            if isinstance(self.default, str):
                sql += f" DEFAULT '{self.default}'"
            elif isinstance(self.default, bool):
                sql += f" DEFAULT {1 if self.default else 0}"
            else:
                sql += f" DEFAULT {self.default}"

        return sql
