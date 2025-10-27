"""
Test file structure and basic imports for EduVerse API
"""

import os
import sys

def test_file_structure():
    """Test that required files exist"""
    print("📁 Testing file structure...")
    
    # Change to backend directory for relative path checking
    os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    required_files = [
        "main.py",
        "app/main.py", 
        "app/core/config.py",
        "app/core/database.py",
        "app/core/logging.py",
        "app/api/v1/api.py",
        "app/api/v1/endpoints/auth.py",
        "app/api/v1/endpoints/courses.py",
        "app/api/v1/endpoints/app_updates.py",
        "app/models/user.py",
        "app/models/course.py",
        "app/schemas/auth.py",
        "app/services/auth_service.py",
        "app/services/email_service.py",
        "requirements.txt",
        "Dockerfile",
    ]
    
    missing_files = []
    found_files = []
    
    for file_path in required_files:
        if os.path.exists(file_path):
            found_files.append(file_path)
            print(f"✅ FOUND - {file_path}")
        else:
            missing_files.append(file_path)
            print(f"❌ MISSING - {file_path}")
    
    print(f"\n📊 Summary: {len(found_files)}/{len(required_files)} files found")
    
    if missing_files:
        print(f"\n⚠️  Missing files:")
        for file_path in missing_files:
            print(f"   - {file_path}")
    
    return len(missing_files) == 0

def test_imports():
    """Test that key modules can be imported"""
    print("\n📦 Testing imports...")
    
    modules_to_test = [
        ("json", "JSON support"),
        ("datetime", "Date/time support"),
        ("os", "OS interface"),
        ("sys", "System interface"),
    ]
    
    success_count = 0
    
    for module_name, description in modules_to_test:
        try:
            __import__(module_name)
            print(f"✅ IMPORT - {description}: {module_name}")
            success_count += 1
        except ImportError:
            print(f"❌ MISSING - {description}: {module_name}")
    
    print(f"\n📊 Import Summary: {success_count}/{len(modules_to_test)} modules imported")
    return success_count == len(modules_to_test)

def test_app_structure():
    """Test application structure"""
    print("\n🏗️  Testing application structure...")
    
    directories = [
        "app",
        "app/core",
        "app/api",
        "app/api/v1",
        "app/api/v1/endpoints",
        "app/models",
        "app/schemas", 
        "app/services",
        "app/templates",
        "app/templates/emails",
        "tests",
    ]
    
    found_dirs = []
    missing_dirs = []
    
    for dir_path in directories:
        if os.path.isdir(dir_path):
            found_dirs.append(dir_path)
            print(f"✅ DIR - {dir_path}")
        else:
            missing_dirs.append(dir_path)
            print(f"❌ MISSING DIR - {dir_path}")
    
    print(f"\n📊 Directory Summary: {len(found_dirs)}/{len(directories)} directories found")
    return len(missing_dirs) == 0

if __name__ == "__main__":
    print("🎓 EduVerse Backend Structure Test")
    print("=" * 50)
    
    all_passed = True
    
    all_passed &= test_file_structure()
    all_passed &= test_imports()
    all_passed &= test_app_structure()
    
    print("\n" + "=" * 50)
    
    if all_passed:
        print("✨ All critical tests passed!")
    else:
        print("⚠️  Some tests failed. Please check the missing files/directories.")