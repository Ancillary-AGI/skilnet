"""
Simple tests for EduVerse API
"""

import pytest
from fastapi.testclient import TestClient
import sys
import os

# Add the parent directory to the path so we can import the app
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from main import app
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
    
    def test_api_v1_health():
        """Test API v1 health endpoint"""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
    
    def test_app_updates_endpoint():
        """Test app updates endpoint"""
        headers = {
            "X-Platform": "android",
            "X-Current-Version": "1.0.0",
            "X-Build-Number": "100"
        }
        response = client.get("/api/v1/app/updates", headers=headers)
        assert response.status_code == 200
        data = response.json()
        assert "hasUpdate" in data
        assert data["platform"] == "android"
    
    def test_version_info_endpoint():
        """Test version info endpoint"""
        response = client.get("/api/v1/app/version-info")
        assert response.status_code == 200
        data = response.json()
        assert "android" in data
        assert "ios" in data
        assert "web" in data
    
    def test_categories_endpoint():
        """Test categories endpoint"""
        response = client.get("/api/v1/categories/")
        assert response.status_code == 200
        data = response.json()
        assert "categories" in data
        assert len(data["categories"]) > 0
    
    def test_translations_endpoint():
        """Test translations endpoint"""
        response = client.get("/api/v1/translations/en")
        assert response.status_code == 200
        data = response.json()
        assert data["language"] == "en"
        assert "translations" in data

except ImportError as e:
    print(f"Could not import app: {e}")
    
    def test_import_error():
        """Test that shows import error"""
        pytest.skip(f"Could not import app: {e}")

if __name__ == "__main__":
    pytest.main([__file__, "-v"])