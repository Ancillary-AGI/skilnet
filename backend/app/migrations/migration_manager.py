import asyncio
import json
import argparse
import sys
from typing import Dict, List, Any, Optional, Tuple
from sqlmodel import SQLModel, Field, create_engine, Session
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
import os

class MigrationRecord(SQLModel, table=True):
    """Record of applied migrations"""
    __tablename__ = "migrations"

    id: int = Field(primary_key=True)
    model_name: str = Field(index=True, nullable=False)
    version: int = Field(nullable=False)
    schema_definition: str = Field(nullable=False)
    operations: str = Field(nullable=False)
    applied_at: str = Field(default_factory=lambda: str(asyncio.get_event_loop().time()))

class MigrationManager:
    """Simplified migration manager for SQLModel"""

    def __init__(self, database_url: str):
        self.database_url = database_url
        self.engine = create_async_engine(database_url, echo=False)
        self.async_session = sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )

    async def initialize(self):
        """Create migrations table if it doesn't exist"""
        async with self.engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)

    async def apply_migrations(self):
        """Apply all pending migrations"""
        from app.models.user import User
        from app.models.course import Course, Module, Lesson, Enrollment, LessonProgress, CourseReview
        from app.models.category import Category
        from app.models.profile import Profile
        from app.models.subscription import Subscription

        models = [User, Course, Module, Lesson, Enrollment, LessonProgress, CourseReview,
                 Category, Profile, Subscription, MigrationRecord]

        async with self.engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)

        print("✓ Database tables created successfully")

    async def reset_database(self):
        """Reset database by dropping all tables"""
        async with self.engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.drop_all)
        print("✓ Database reset complete")

    async def show_status(self):
        """Show current database status"""
        async with AsyncSession(self.engine) as session:
            try:
                # Check if migrations table exists
                result = await session.execute(
                    "SELECT name FROM sqlite_master WHERE type='table' AND name='migrations'"
                )
                tables = result.fetchall()

                if tables:
                    print("✓ Migrations table exists")
                else:
                    print("⚠ Migrations table does not exist")

                # List all tables
                result = await session.execute(
                    "SELECT name FROM sqlite_master WHERE type='table'"
                )
                tables = result.fetchall()

                print(f"\nCurrent tables ({len(tables)}):")
                for table in tables:
                    print(f"  - {table[0]}")

            except Exception as e:
                print(f"Error checking database status: {e}")
async def run_migrations():
    """Run migrations based on command line arguments"""
    parser = argparse.ArgumentParser(description="Database Migration Manager")
    parser.add_argument("--action", choices=["migrate", "reset", "status"],
                       default="migrate", help="Action to perform")
    parser.add_argument("--database-url", default="sqlite:///./database.db",
                       help="Database connection URL")

    args = parser.parse_args()

    # Initialize migration manager
    manager = MigrationManager(args.database_url)
    await manager.initialize()

    # Perform requested action
    if args.action == "migrate":
        await manager.apply_migrations()
        print("✓ Migration completed")

    elif args.action == "reset":
        confirm = input("Are you sure you want to reset the database? This will drop all tables! (y/N): ")
        if confirm.lower() == 'y':
            await manager.reset_database()
        else:
            print("Reset cancelled")

    elif args.action == "status":
        await manager.show_status()

async def main():
    try:
        await run_migrations()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
