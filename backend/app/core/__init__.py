"""
Core module for EduVerse platform
"""

# Configuration
from .config import Settings, settings

# Database
from .database import get_db, create_tables

# Security
from .security import get_current_user, get_current_active_user

# Logging
from .logging import get_logger

__all__ = [
    "Settings",
    "settings",
    "get_db",
    "create_tables",
    "get_current_user",
    "get_current_active_user",
    "get_logger",
]
