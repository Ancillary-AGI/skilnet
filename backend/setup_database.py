#!/usr/bin/env python3
"""
Database setup script for EduVerse
Supports PostgreSQL, MySQL, MongoDB, and SQLite
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the backend directory to Python path
sys.path.insert(0, str(Path(__file__).parent))

from app.core.database_config import db_config, DatabaseType, CLOUD_DATABASE_PRESETS
from app.core.database import init_database, check_database_connection
from app.services.initialization_service import InitializationService

class DatabaseSetup:
    """Database setup and configuration utility"""
    
    def __init__(self):
        self.init_service = InitializationService()
    
    async def setup_database(self):
        """Main database setup function"""
        print("🎓 EduVerse Database Setup")
        print("=" * 50)
        
        # Show current configuration
        print(f"📊 Current Database Type: {db_config.DB_TYPE.value}")
        print(f"🔗 Database URL: {self._mask_password(db_config.get_database_url())}")
        
        # Check if we can connect
        print("\n🔍 Testing database connection...")
        
        if await check_database_connection():
            print("✅ Database connection successful!")
            
            # Initialize tables
            print("\n🏗️  Creating database tables...")
            await init_database()
            print("✅ Database tables created successfully!")
            
            # Run initialization
            print("\n🚀 Running full system initialization...")
            status = await self.init_service.initialize_all()
            
            print(f"\n📊 Setup Status: {status['status']}")
            print("Systems:")
            for system, status_val in status['systems'].items():
                icon = "✅" if status_val else "❌"
                print(f"  {icon} {system.title()}")
            
            return True
            
        else:
            print("❌ Database connection failed!")
            print("\n💡 Troubleshooting tips:")
            await self._show_troubleshooting_tips()
            return False
    
    def _mask_password(self, url: str) -> str:
        """Mask password in database URL for display"""
        if "://" in url and "@" in url:
            parts = url.split("://")
            if len(parts) == 2:
                protocol = parts[0]
                rest = parts[1]
                if "@" in rest:
                    auth_part, host_part = rest.split("@", 1)
                    if ":" in auth_part:
                        user, _ = auth_part.split(":", 1)
                        return f"{protocol}://{user}:***@{host_part}"
        return url
    
    async def _show_troubleshooting_tips(self):
        """Show troubleshooting tips based on database type"""
        
        if db_config.DB_TYPE == DatabaseType.POSTGRESQL:
            print("\n🐘 PostgreSQL Troubleshooting:")
            print("1. Make sure PostgreSQL is running:")
            print("   sudo systemctl start postgresql")
            print("2. Create database and user:")
            print(f"   sudo -u postgres createdb {db_config.POSTGRES_DB}")
            print(f"   sudo -u postgres createuser {db_config.POSTGRES_USER}")
            print("3. Set password:")
            print(f"   sudo -u postgres psql -c \"ALTER USER {db_config.POSTGRES_USER} PASSWORD '{db_config.POSTGRES_PASSWORD}';\"")
            print("4. Grant permissions:")
            print(f"   sudo -u postgres psql -c \"GRANT ALL PRIVILEGES ON DATABASE {db_config.POSTGRES_DB} TO {db_config.POSTGRES_USER};\"")
            
        elif db_config.DB_TYPE == DatabaseType.MYSQL:
            print("\n🐬 MySQL Troubleshooting:")
            print("1. Make sure MySQL is running:")
            print("   sudo systemctl start mysql")
            print("2. Create database and user:")
            print("   mysql -u root -p")
            print(f"   CREATE DATABASE {db_config.MYSQL_DB};")
            print(f"   CREATE USER '{db_config.MYSQL_USER}'@'localhost' IDENTIFIED BY '{db_config.MYSQL_PASSWORD}';")
            print(f"   GRANT ALL PRIVILEGES ON {db_config.MYSQL_DB}.* TO '{db_config.MYSQL_USER}'@'localhost';")
            print("   FLUSH PRIVILEGES;")
            
        elif db_config.DB_TYPE == DatabaseType.MONGODB:
            print("\n🍃 MongoDB Troubleshooting:")
            print("1. Make sure MongoDB is running:")
            print("   sudo systemctl start mongod")
            print("2. Connect and create user (if authentication is enabled):")
            print("   mongo")
            print(f"   use {db_config.MONGODB_DB}")
            print(f"   db.createUser({{user: '{db_config.MONGODB_USER}', pwd: '{db_config.MONGODB_PASSWORD}', roles: ['readWrite']}})")
            
        elif db_config.DB_TYPE == DatabaseType.SQLITE:
            print("\n📁 SQLite Troubleshooting:")
            print("1. Check file permissions:")
            print(f"   ls -la {db_config.SQLITE_PATH}")
            print("2. Create directory if needed:")
            print(f"   mkdir -p {Path(db_config.SQLITE_PATH).parent}")
    
    def show_cloud_presets(self):
        """Show available cloud database presets"""
        print("\n☁️  Available Cloud Database Presets:")
        print("=" * 50)
        
        for preset_name, config in CLOUD_DATABASE_PRESETS.items():
            print(f"\n📊 {preset_name.replace('_', ' ').title()}:")
            print(f"   Database Type: {config.get('DB_TYPE', 'N/A')}")
            if 'DATABASE_URL' in config:
                print(f"   URL Pattern: {config['DATABASE_URL']}")
            else:
                print(f"   Host Pattern: {config.get('POSTGRES_HOST', config.get('MYSQL_HOST', 'N/A'))}")
        
        print("\n💡 To use a preset, set these environment variables:")
        print("   DB_TYPE=postgresql")
        print("   DATABASE_URL=your-cloud-database-url")
    
    async def test_all_connections(self):
        """Test connections to all configured databases"""
        print("🧪 Testing All Database Connections")
        print("=" * 50)
        
        original_type = db_config.DB_TYPE
        
        for db_type in DatabaseType:
            print(f"\n🔍 Testing {db_type.value}...")
            
            # Temporarily change database type
            db_config.DB_TYPE = db_type
            
            try:
                if await check_database_connection():
                    print(f"✅ {db_type.value} connection successful")
                else:
                    print(f"❌ {db_type.value} connection failed")
            except Exception as e:
                print(f"❌ {db_type.value} connection error: {e}")
        
        # Restore original type
        db_config.DB_TYPE = original_type

async def main():
    """Main setup function"""
    setup = DatabaseSetup()
    
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "setup":
            success = await setup.setup_database()
            sys.exit(0 if success else 1)
            
        elif command == "test":
            await setup.test_all_connections()
            
        elif command == "presets":
            setup.show_cloud_presets()
            
        elif command == "help":
            print("🎓 EduVerse Database Setup")
            print("\nCommands:")
            print("  setup    - Set up database and initialize tables")
            print("  test     - Test all database connections")
            print("  presets  - Show cloud database presets")
            print("  help     - Show this help message")
            print("\nExamples:")
            print("  python setup_database.py setup")
            print("  python setup_database.py test")
            print("  python setup_database.py presets")
            
        else:
            print(f"❌ Unknown command: {command}")
            print("Run 'python setup_database.py help' for available commands")
            sys.exit(1)
    else:
        # Default: run setup
        success = await setup.setup_database()
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    asyncio.run(main())