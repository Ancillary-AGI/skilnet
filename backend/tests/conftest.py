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
os.environ["SQLITE_PATH"] = "./test.db"
os.environ["SECRET_KEY"] = "test-secret-key-for-testing-only"
os.environ["DEBUG"] = "true"

try:
    from app.main import app
    from fastapi.testclient import TestClient
    
    @pytest.fixture
    def client():
        """Test client fixture"""
        return TestClient(app)
    
    @pytest.fixture
    def event_loop():
        """Create an instance of the default event loop for the test session."""
        loop = asyncio.get_event_loop_policy().new_event_loop()
        yield loop
        loop.close()

except ImportError as e:
    print(f"Warning: Could not import app for testing: {e}")
    
    @pytest.fixture
    def client():
        """Mock client fixture when app import fails"""
        return None