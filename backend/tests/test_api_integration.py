"""
API integration tests for EduVerse platform
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

if __name__ == "__main__":
    print("🎓 EduVerse API Integration Test Suite")
    print("=" * 50)
    
    test_api_endpoints()
    
    print("\n" + "=" * 50)
    print("✨ Integration test suite completed!")