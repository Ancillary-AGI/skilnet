"""
Basic test script for EduVerse API
"""

import sys
import os
import requests
import json

def test_api_endpoints():
    """Test basic API endpoints"""
    base_url = "http://localhost:8000"
    
    print("🧪 Testing EduVerse API endpoints...")
    
    # Test endpoints that don't require authentication
    endpoints = [
        ("/", "Root endpoint"),
        ("/health", "Health check"),
        ("/api/info", "API info"),
        ("/api/v1/health", "API v1 health"),
        ("/api/v1/categories/", "Categories"),
        ("/api/v1/translations/en", "Translations"),
    ]
    
    for endpoint, description in endpoints:
        try:
            response = requests.get(f"{base_url}{endpoint}", timeout=5)
            status = "✅ PASS" if response.status_code == 200 else f"❌ FAIL ({response.status_code})"
            print(f"{status} - {description}: {endpoint}")
            
            if response.status_code == 200 and endpoint != "/":
                try:
                    data = response.json()
                    print(f"    Response keys: {list(data.keys())}")
                except:
                    print(f"    Response length: {len(response.text)} chars")
            
        except requests.exceptions.ConnectionError:
            print(f"🔌 SKIP - {description}: Server not running")
        except Exception as e:
            print(f"❌ ERROR - {description}: {str(e)}")
    
    # Test app updates endpoint with headers
    print("\n🔄 Testing app updates endpoint...")
    try:
        headers = {
            "X-Platform": "android",
            "X-Current-Version": "1.0.0",
            "X-Build-Number": "100"
        }
        response = requests.get(f"{base_url}/api/v1/app/updates", headers=headers, timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ PASS - App updates check")
            print(f"    Has update: {data.get('hasUpdate', 'N/A')}")
            print(f"    Platform: {data.get('platform', 'N/A')}")
        else:
            print(f"❌ FAIL - App updates check ({response.status_code})")
    except requests.exceptions.ConnectionError:
        print("🔌 SKIP - App updates: Server not running")
    except Exception as e:
        print(f"❌ ERROR - App updates: {str(e)}")

def test_file_structure():
    """Test that required files exist"""
    print("\n📁 Testing file structure...")
    
    required_files = [
        "main.py",
        "app/main.py",
        "app/core/config.py",
        "app/core/database.py",
        "app/api/v1/api.py",
        "app/models/user.py",
        "requirements.txt",
    ]
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ FOUND - {file_path}")
        else:
            print(f"❌ MISSING - {file_path}")

def test_imports():
    """Test that key modules can be imported"""
    print("\n📦 Testing imports...")
    
    modules_to_test = [
        ("fastapi", "FastAPI framework"),
        ("sqlalchemy", "SQLAlchemy ORM"),
        ("pydantic", "Pydantic validation"),
        ("uvicorn", "ASGI server"),
    ]
    
    for module_name, description in modules_to_test:
        try:
            __import__(module_name)
            print(f"✅ IMPORT - {description}: {module_name}")
        except ImportError:
            print(f"❌ MISSING - {description}: {module_name}")

if __name__ == "__main__":
    print("🎓 EduVerse API Test Suite")
    print("=" * 50)
    
    test_file_structure()
    test_imports()
    test_api_endpoints()
    
    print("\n" + "=" * 50)
    print("✨ Test suite completed!")
    print("\n💡 To run the API server:")
    print("   python main.py")
    print("\n💡 To run with uvicorn:")
    print("   uvicorn main:app --reload")