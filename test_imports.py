#!/usr/bin/env python3
"""
Test script to check imports and identify issues
"""

import sys
import os

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def test_imports():
    """Test basic imports"""
    try:
        print("Testing basic imports...")

        # Test FastAPI
        from fastapi import FastAPI
        print("✓ FastAPI imported successfully")

        # Test SQLAlchemy
        from sqlalchemy import create_engine
        print("✓ SQLAlchemy imported successfully")

        # Test Pydantic
        from pydantic import BaseModel
        print("✓ Pydantic imported successfully")

        # Test app imports
        print("\nTesting app imports...")

        from app.core.config import settings
        print("✓ Config imported successfully")

        from app.core.database import Base, get_db
        print("✓ Database imported successfully")

        from app.models.user import User
        print("✓ User model imported successfully")

        from app.services.auth_service import AuthService
        print("✓ AuthService imported successfully")

        from app.api.v1.api import api_router
        print("✓ API router imported successfully")

        print("\n🎉 All imports successful!")

    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

    return True

if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)
