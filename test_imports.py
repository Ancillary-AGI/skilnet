#!/usr/bin/env python3
"""
Test script to check imports and identify issues
"""

import os
import sys
from importlib import import_module
from importlib.util import find_spec

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

BASIC_MODULES = [
    ("fastapi", "FastAPI imported successfully", ["FastAPI"]),
    ("sqlalchemy", "SQLAlchemy imported successfully", ["create_engine"]),
    ("pydantic", "Pydantic imported successfully", ["BaseModel"]),
]

APP_MODULES = [
    ("app.core.config", "Config imported successfully", ["settings"]),
    ("app.core.database", "Database imported successfully", ["Base", "get_db"]),
    ("app.models.user", "User model imported successfully", ["User"]),
    ("app.services.auth_service", "AuthService imported successfully", ["AuthService"]),
    ("app.api.v1.api", "API router imported successfully", ["api_router"]),
]


def _module_available(module_path: str) -> bool:
    return find_spec(module_path) is not None


def _validate_module(module_path: str, description: str, attributes: list[str]) -> bool:
    if not _module_available(module_path):
        print(f"❌ Missing module: {module_path}")
        return False
    
    module = import_module(module_path)
    missing = [attr for attr in attributes if not hasattr(module, attr)]
    if missing:
        print(f"❌ Missing attributes {missing} in module: {module_path}")
        return False
    
    print(f"✓ {description}")
    return True


def test_imports():
    """Test basic and application-specific imports"""
    print("Testing basic imports...")
    results = [
        _validate_module(module, description, attrs)
        for module, description, attrs in BASIC_MODULES
    ]
    
    print("\nTesting app imports...")
    results.extend(
        _validate_module(module, description, attrs)
        for module, description, attrs in APP_MODULES
    )
    
    success = all(results)
    if success:
        print("\n🎉 All imports successful!")
    else:
        print("\n⚠️  Some imports failed.")
    return success

if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)
