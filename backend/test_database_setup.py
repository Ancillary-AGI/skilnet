#!/usr/bin/env python3
"""
Simple test for database configuration without full app dependencies
"""

import os
from enum import Enum

class DatabaseType(str, Enum):
    SQLITE = "sqlite"
    POSTGRESQL = "postgresql"
    MYSQL = "mysql"
    MONGODB = "mongodb"

def test_database_config():
    """Test database configuration"""
    print("🎓 EduVerse Database Configuration Test")
    print("=" * 50)
    
    # Test environment variables
    db_type = os.getenv("DB_TYPE", "postgresql")
    print(f"📊 Database Type: {db_type}")
    
    # Test database URLs
    if db_type == "postgresql":
        host = os.getenv("POSTGRES_HOST", "localhost")
        port = os.getenv("POSTGRES_PORT", "5432")
        db = os.getenv("POSTGRES_DB", "eduverse")
        user = os.getenv("POSTGRES_USER", "eduverse_user")
        password = os.getenv("POSTGRES_PASSWORD", "eduverse_password")
        
        url = f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{db}"
        print(f"🔗 PostgreSQL URL: {url}")
        
    elif db_type == "mysql":
        host = os.getenv("MYSQL_HOST", "localhost")
        port = os.getenv("MYSQL_PORT", "3306")
        db = os.getenv("MYSQL_DB", "eduverse")
        user = os.getenv("MYSQL_USER", "eduverse_user")
        password = os.getenv("MYSQL_PASSWORD", "eduverse_password")
        
        url = f"mysql+aiomysql://{user}:{password}@{host}:{port}/{db}"
        print(f"🔗 MySQL URL: {url}")
        
    elif db_type == "sqlite":
        path = os.getenv("SQLITE_PATH", "./database.db")
        url = f"sqlite+aiosqlite:///{path}"
        print(f"🔗 SQLite URL: {url}")
        
    elif db_type == "mongodb":
        host = os.getenv("MONGODB_HOST", "localhost")
        port = os.getenv("MONGODB_PORT", "27017")
        db = os.getenv("MONGODB_DB", "eduverse")
        
        url = f"mongodb://{host}:{port}/{db}"
        print(f"🔗 MongoDB URL: {url}")
    
    # Test storage configuration
    storage_provider = os.getenv("STORAGE_PROVIDER", "aws_s3")
    print(f"☁️  Storage Provider: {storage_provider}")
    
    if storage_provider == "aws_s3":
        bucket = os.getenv("AWS_S3_BUCKET", "eduverse-storage")
        region = os.getenv("AWS_REGION", "us-east-1")
        print(f"📁 S3 Bucket: {bucket} in {region}")
        
    elif storage_provider == "local":
        path = os.getenv("LOCAL_STORAGE_PATH", "./uploads")
        print(f"📁 Local Storage: {path}")
    
    print("\n✅ Configuration test completed!")
    print("\n💡 Next steps:")
    print("1. Install dependencies: pip install -r requirements.txt")
    print("2. Copy .env.example to .env and configure")
    print("3. Run: python setup_database.py setup")

if __name__ == "__main__":
    test_database_config()