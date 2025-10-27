#!/usr/bin/env python3
"""
Test runner for EduVerse backend tests
"""

import sys
import os
import subprocess
from pathlib import Path

def run_structure_tests():
    """Run structure tests"""
    print("🏗️  Running structure tests...")
    try:
        result = subprocess.run([sys.executable, "test_structure.py"], 
                              cwd=Path(__file__).parent, 
                              capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Structure tests failed: {e}")
        return False

def run_unit_tests():
    """Run unit tests"""
    print("\n🧪 Running unit tests...")
    try:
        result = subprocess.run([sys.executable, "-m", "pytest", ".", "-v"], 
                              cwd=Path(__file__).parent, 
                              capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Unit tests failed: {e}")
        return False

def run_integration_tests():
    """Run integration tests"""
    print("\n🔗 Running integration tests...")
    print("💡 Note: Integration tests require the backend server to be running")
    print("   Start server with: python main.py")
    
    try:
        result = subprocess.run([sys.executable, "test_complete_integration.py"], 
                              cwd=Path(__file__).parent, 
                              capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Integration tests failed: {e}")
        return False

def main():
    """Main test runner"""
    print("🎓 EduVerse Backend Test Suite")
    print("=" * 50)
    
    all_passed = True
    
    # Run structure tests
    all_passed &= run_structure_tests()
    
    # Run unit tests
    all_passed &= run_unit_tests()
    
    # Run integration tests (optional)
    print("\n" + "=" * 50)
    print("🔗 Integration Tests (optional)")
    print("These tests require the backend server to be running.")
    
    response = input("Run integration tests? (y/N): ").lower().strip()
    if response in ['y', 'yes']:
        all_passed &= run_integration_tests()
    else:
        print("⏭️  Skipping integration tests")
    
    print("\n" + "=" * 50)
    
    if all_passed:
        print("✅ All tests passed!")
        return 0
    else:
        print("❌ Some tests failed!")
        return 1

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)