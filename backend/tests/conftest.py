"""
Test configuration for EduVerse backend
"""

import pytest
import asyncio
import os
import sys
from pathlib import Path

# Add the parent directory to the path so we can import the app
sys.path.insert(0, str(Path(__file__).parent.parent))

# Set test environment variables
os.environ["DB_TYPE"] = "sqlite"
os.environ["SQLITE_PATH"] = ":memory:"
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
def db_session():
    """Database session fixture"""
    from app.core.database import AsyncSessionLocal

    session = AsyncSessionLocal()
    try:
        yield session
    finally:
        # Note: In a real test, you'd want to properly close the session
        # But for simplicity with pytest-asyncio, we'll let it be
        pass

try:
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

except ImportError as e:
    print(f"Warning: Could not import app for testing: {e}")

    @pytest.fixture
    def client():
        """Mock client fixture when app import fails"""
        return None

    @pytest.fixture
    async def async_client():
        """Mock async client fixture when app import fails"""
        return None
