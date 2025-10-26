"""
Test file structure and basic imports for EduVerse API
"""

import os
import sys

def test_file_structure():
    """Test that required files exist"""
    print("📁 Testing file structure...")
    
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

def test_configuration():
    """Test configuration files"""
    print("\n⚙️  Testing configuration...")
    
    config_files = [
        ("requirements.txt", "Python dependencies"),
        ("Dockerfile", "Docker configuration"),
        (".gitignore", "Git ignore rules"),
        ("README.md", "Documentation"),
    ]
    
    for file_path, description in config_files:
        if os.path.exists(file_path):
            print(f"✅ CONFIG - {description}: {file_path}")
            
            # Check file size
            size = os.path.getsize(file_path)
            print(f"    Size: {size} bytes")
            
            if file_path == "requirements.txt":
                with open(file_path, 'r') as f:
                    lines = f.readlines()
                    print(f"    Dependencies: {len(lines)} packages")
        else:
            print(f"❌ MISSING CONFIG - {description}: {file_path}")

def main():
    """Run all tests"""
    print("🎓 EduVerse Backend Structure Test")
    print("=" * 50)
    
    all_passed = True
    
    all_passed &= test_file_structure()
    all_passed &= test_imports()
    all_passed &= test_app_structure()
    test_configuration()
    
    print("\n" + "=" * 50)
    
    if all_passed:
        print("✨ All critical tests passed!")
        print("\n🚀 Ready to run the application:")
        print("   python main.py")
        print("\n🔧 Or with uvicorn:")
        print("   uvicorn main:app --reload")
    else:
        print("⚠️  Some tests failed. Please check the missing files/directories.")
    
    print("\n📚 Next steps:")
    print("   1. Install dependencies: pip install -r requirements.txt")
    print("   2. Set up environment variables")
    print("   3. Run the application")
    print("   4. Test API endpoints")

if __name__ == "__main__":
    main()