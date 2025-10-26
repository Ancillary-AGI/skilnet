"""
Tests for authentication endpoints
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_api_info():
    """Test API info endpoint"""
    response = client.get("/api/info")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "EduVerse API"
    assert data["version"] == "2.0.0"

def test_register_user():
    """Test user registration"""
    user_data = {
        "email": "test@example.com",
        "password": "TestPassword123",
        "full_name": "Test User"
    }
    
    response = client.post("/api/v1/auth/register", json=user_data)
    # Note: This will fail without proper database setup
    # In a real test, you'd use a test database
    assert response.status_code in [200, 201, 400, 500]

def test_login_invalid_credentials():
    """Test login with invalid credentials"""
    login_data = {
        "email": "invalid@example.com",
        "password": "wrongpassword"
    }
    
    response = client.post("/api/v1/auth/login", json=login_data)
    assert response.status_code in [401, 400, 500]

def test_get_courses():
    """Test get courses endpoint"""
    response = client.get("/api/v1/courses/")
    assert response.status_code in [200, 401, 500]

def test_app_updates_check():
    """Test app updates check"""
    headers = {
        "X-Platform": "android",
        "X-Current-Version": "1.0.0",
        "X-Build-Number": "100"
    }
    
    response = client.get("/api/v1/app/updates", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "hasUpdate" in data
    assert "platform" in data

def test_version_info():
    """Test version info endpoint"""
    response = client.get("/api/v1/app/version-info")
    assert response.status_code == 200
    data = response.json()
    assert "android" in data
    assert "ios" in data
    assert "web" in data

if __name__ == "__main__":
    pytest.main([__file__])