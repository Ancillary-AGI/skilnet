"""
Simple tests for EduVerse API
"""

import os
import sys

import pytest
from fastapi.testclient import TestClient

# Add the parent directory to the path so we can import the app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.main import app


def test_basic_functionality():
    """Test basic Python functionality"""
    assert 2 + 2 == 4
    assert "EduVerse".lower() == "eduverse"

client = TestClient(app)


def test_root_endpoint():
    """Test root endpoint returns HTML"""
    response = client.get("/")
    assert response.status_code == 200
    assert "EduVerse" in response.text


def test_health_endpoint():
    """Test health endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "EduVerse API"


def test_api_info_endpoint():
    """Test API info endpoint"""
    response = client.get("/api/info")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "EduVerse API"
    assert data["version"] == "2.0.0"

if __name__ == "__main__":
    pytest.main([__file__, "-v"])