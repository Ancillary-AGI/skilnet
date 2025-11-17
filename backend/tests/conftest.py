"""
Test configuration for EduVerse backend
"""

import asyncio
import os
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from httpx import AsyncClient

# Add the parent directory to the path so we can import the app
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.main import app

# Set test environment variables
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["SECRET_KEY"] = "test-secret-key-for-testing-only"
os.environ["DEBUG"] = "true"
os.environ["TESTING"] = "true"

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session", autouse=True)
async def setup_test_database():
    """Set up test database"""
    from app.core.database import init_database, create_tables

    # Initialize database
    await init_database()
    await create_tables()
    print("✅ Test database setup completed")

@pytest.fixture
async def db_session():
    """Database session fixture with transaction rollback"""
    from app.core.database import AsyncSessionLocal

    async with AsyncSessionLocal() as session:
        async with session.begin():
            yield session

from app.main import app
from fastapi.testclient import TestClient
from httpx import AsyncClient

@pytest.fixture
def client():
    """Test client fixture"""
    return TestClient(app)


@pytest.fixture
def async_client():
    """Async test client fixture"""
    return AsyncClient(app=app, base_url="http://testserver")
