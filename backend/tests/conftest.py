"""
Test configuration and fixtures
"""

import pytest
import asyncio
from typing import AsyncGenerator
import os
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core.database import get_db, Base
from app.core.config import settings

# Test database URL
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

# Create test engine
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    echo=False,
    poolclass=StaticPool,
    connect_args={"check_same_thread": False}
)

# Create test session factory
TestSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False
)


class TestDatabase:
    """Test database management"""
    
    @staticmethod
    async def create_tables():
        """Create all database tables"""
        async with test_engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    
    @staticmethod
    async def drop_tables():
        """Drop all database tables"""
        async with test_engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
    
    @staticmethod
    async def clear_tables():
        """Clear all data from tables"""
        async with test_engine.begin() as conn:
            for table in reversed(Base.metadata.sorted_tables):
                await conn.execute(table.delete())


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def setup_test_db():
    """Set up test database"""
    await TestDatabase.create_tables()
    yield
    await TestDatabase.drop_tables()


@pytest.fixture
async def db(setup_test_db) -> AsyncGenerator[AsyncSession, None]:
    """Get test database session"""
    async with TestSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
    
    # Clean up after each test
    await TestDatabase.clear_tables()


async def override_get_db():
    """Override database dependency for testing"""
    async with TestSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


@pytest.fixture
async def client(db: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Get test client with database override"""
    app.dependency_overrides[get_db] = override_get_db
    
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
    
    app.dependency_overrides.clear()


@pytest.fixture
def mock_settings():
    """Mock application settings for testing"""
    test_settings = settings.copy()
    test_settings.DATABASE_URL = TEST_DATABASE_URL
    test_settings.SECRET_KEY = "test-secret-key-for-testing-only"
    test_settings.DEBUG = True
    return test_settings


# Performance testing fixtures
@pytest.fixture
def performance_monitor():
    """Monitor performance during tests"""
    import time
    import psutil
    import os
    
    process = psutil.Process(os.getpid())
    start_time = time.time()
    start_memory = process.memory_info().rss
    start_cpu = process.cpu_percent()
    
    yield
    
    end_time = time.time()
    end_memory = process.memory_info().rss
    end_cpu = process.cpu_percent()
    
    execution_time = end_time - start_time
    memory_usage = end_memory - start_memory
    cpu_usage = end_cpu - start_cpu
    
    print(f"\nPerformance Metrics:")
    print(f"Execution Time: {execution_time:.2f}s")
    print(f"Memory Usage: {memory_usage / 1024 / 1024:.2f}MB")
    print(f"CPU Usage: {cpu_usage:.2f}%")


# Mock data fixtures
@pytest.fixture
def mock_course_data():
    """Mock course data for testing"""
    return {
        "id": "test-course-id",
        "title": "Test Course",
        "description": "A comprehensive test course",
        "instructor": "Test Instructor",
        "category": "technology",
        "difficulty": "intermediate",
        "duration_hours": 20,
        "price": 99.99,
        "rating": 4.7,
        "students": 1500,
        "hasVR": True,
        "hasAR": True,
        "modules": [
            {
                "id": "module-1",
                "title": "Introduction",
                "lessons": [
                    {
                        "id": "lesson-1",
                        "title": "Getting Started",
                        "duration": 15,
                        "type": "video"
                    }
                ]
            }
        ]
    }


@pytest.fixture
def mock_user_data():
    """Mock user data for testing"""
    return {
        "id": "test-user-id",
        "email": "test@example.com",
        "username": "testuser",
        "first_name": "Test",
        "last_name": "User",
        "level": 5,
        "experience_points": 2500,
        "badges": ["early_adopter", "vr_explorer"],
        "subscription_tier": "premium",
        "learning_style": "visual",
        "preferred_language": "en"
    }


# Load testing fixtures
@pytest.fixture
def load_test_config():
    """Configuration for load testing"""
    return {
        "concurrent_users": 100,
        "test_duration": 60,  # seconds
        "ramp_up_time": 10,   # seconds
        "endpoints_to_test": [
            "/api/v1/courses/",
            "/api/v1/auth/me",
            "/api/v1/users/profile"
        ]
    }


# Security testing fixtures
@pytest.fixture
def security_test_payloads():
    """Security test payloads for vulnerability testing"""
    return {
        "sql_injection": [
            "'; DROP TABLE users; --",
            "' OR '1'='1",
            "'; UPDATE users SET is_superuser=true; --"
        ],
        "xss_payloads": [
            "<script>alert('xss')</script>",
            "javascript:alert('xss')",
            "<img src=x onerror=alert('xss')>"
        ],
        "path_traversal": [
            "../../../etc/passwd",
            "..\\..\\..\\windows\\system32\\config\\sam",
            "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd"
        ]
    }


# Cleanup fixtures
@pytest.fixture(autouse=True)
async def cleanup_test_files():
    """Clean up test files after each test"""
    yield
    
    # Clean up uploaded test files
    test_dirs = ["./uploads/test", "./temp/test", "./models/test"]
    for test_dir in test_dirs:
        if os.path.exists(test_dir):
            import shutil
            shutil.rmtree(test_dir)


# Mock external services
@pytest.fixture
def mock_external_services(monkeypatch):
    """Mock external services for testing"""
    
    async def mock_send_email(*args, **kwargs):
        return {"status": "sent", "message_id": "test-message-id"}
    
    async def mock_ai_generation(*args, **kwargs):
        return {"content": "Mock AI generated content", "confidence": 0.95}
    
    async def mock_video_processing(*args, **kwargs):
        return {"status": "processed", "url": "http://test.com/video.mp4"}
    
    monkeypatch.setattr("app.services.email_service.EmailService.send_email", mock_send_email)
    monkeypatch.setattr("app.services.ai_video_generator.AIVideoGenerator.generate_course_video", mock_ai_generation)
    monkeypatch.setattr("app.services.content_processor.ContentProcessor.process_video", mock_video_processing)