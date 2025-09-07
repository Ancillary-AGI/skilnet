from typing import Any, TypeVar
import asyncpg
import sqlite3
from contextlib import asynccontextmanager
import os

from backend.app.models.base_model import BaseModel

T = TypeVar('T', bound='BaseModel')

class DatabaseConfig:
    def __init__(self, database_url: str = None):
        self.database_url = database_url or os.getenv('DATABASE_URL', 'sqlite:///:memory:')
        self.is_sqlite = 'sqlite' in self.database_url
        
    def get_connection_params(self):
        if self.is_sqlite:
            return {'database': ':memory:'}
        else:
            # Parse PostgreSQL connection string
            url = self.database_url.replace('postgresql://', '')
            if '@' in url:
                auth, host_db = url.split('@', 1)
                user, password = auth.split(':', 1) if ':' in auth else (auth, '')
                host_port, database = host_db.split('/', 1)
                if ':' in host_port:
                    host, port = host_port.split(':', 1)
                else:
                    host, port = host_port, '5432'
                return {
                    'user': user,
                    'password': password,
                    'host': host,
                    'port': port,
                    'database': database
                }
            return {}

class DatabaseConnection:
    _instance = None
    _config = None
    
    def __init__(self, config: DatabaseConfig):
        self.config = config
        self.pool = None
        
    @classmethod
    def get_instance(cls, config = DatabaseConfig()):
        if cls._instance is None:
            cls._instance = cls(config)
        return cls._instance
    
    async def connect(self):
        if self.config.is_sqlite:
            # SQLite doesn't need connection pooling
            return
        else:
            params = self.config.get_connection_params()
            self.pool = await asyncpg.create_pool(**params)
    
    async def disconnect(self):
        if self.pool:
            await self.pool.close()
    
    @asynccontextmanager
    async def get_connection(self):
        if self.config.is_sqlite:
            conn = sqlite3.connect(':memory:')
            conn.row_factory = sqlite3.Row
            # Enable foreign keys for SQLite
            conn.execute("PRAGMA foreign_keys = ON")
            try:
                yield conn
            finally:
                conn.close()
        else:
            async with self.pool.acquire() as conn:
                yield conn

class Field:
    def __init__(self, field_type: str, primary_key: bool = False, autoincrement: bool = False, 
                 unique: bool = False, nullable: bool = True, 
                 default: Any = None, foreign_key: str = None, index: bool = False,
                 after: str = None):
        self.field_type = field_type
        self.primary_key = primary_key
        self.autoincrement = autoincrement
        self.unique = unique
        self.nullable = nullable
        self.default = default() if callable(default) else default
        self.foreign_key = foreign_key
        self.index = index
        self.after = after
    
    def sql_definition(self, name: str, is_sqlite: bool) -> str:
        parts = [name]
        
        # Handle field type differences between databases
        if is_sqlite:
            if self.field_type.upper() == 'SERIAL':
                parts.append('INTEGER')
            else:
                parts.append(self.field_type)
        else:
            parts.append(self.field_type)
        
        if self.primary_key:
            parts.append("PRIMARY KEY")
            if self.autoincrement:
                if is_sqlite:
                    parts.append("AUTOINCREMENT")
                else:
                    parts.append("SERIAL")
        
        if not self.nullable:
            parts.append("NOT NULL")
            
        if self.unique:
            parts.append("UNIQUE")
            
        if self.default is not None:
            if isinstance(self.default, str) and not self.default.startswith("'") and not self.default.startswith("CURRENT"):
                parts.append(f"DEFAULT '{self.default}'")
            else:
                parts.append(f"DEFAULT {self.default}")
        
        if self.foreign_key:
            parts.append(f"REFERENCES {self.foreign_key}")
                
        return " ".join(parts)