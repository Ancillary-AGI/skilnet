"""
EduVerse Backend Application

Advanced E-Learning Platform with VR/AR and AI capabilities
"""

# Version info
__version__ = "1.0.0"
__author__ = "EduVerse Team"
__description__ = "Advanced E-Learning Platform with VR/AR and AI capabilities"

# Core modules
from .core import (
    Settings,
    settings,
    get_db,
    create_tables,
    get_current_user,
    get_current_active_user,
    get_logger
)

# Models
from .models import (
    User,
    Course,
    Category,
    UserProfile
)

# Schemas
from .schemas import (
    UserCreate,
    UserLogin,
    TokenResponse,
    UserResponse,
    CourseCreate,
    CourseResponse
)

# Services (commented out for now - need to implement properly)
# from .services import (
#     EmailService,
#     get_email_service,
#     CacheService,
#     get_cache_service,
#     CategoryService
# )

# API endpoints (commented out for now)
# from .api.v1.endpoints import (
#     auth_router,
#     courses_router,
#     translations_router
# )

__all__ = [
    # Version info
    "__version__",
    "__author__",
    "__description__",

    # Core
    "Settings",
    "settings",
    "get_db",
    "create_tables",
    "get_current_user",
    "get_current_active_user",
    "get_logger",

    # Models
    "User",
    "Course",
    "Category",
    "UserProfile",

    # Schemas
    "UserCreate",
    "UserLogin",
    "TokenResponse",
    "UserResponse",
    "CourseCreate",
    "CourseResponse",

    # Services (commented out)
    # "EmailService",
    # "get_email_service",
    # "CacheService",
    # "get_cache_service",
    # "CategoryService",

    # API endpoints (commented out)
    # "auth_router",
    # "courses_router",
    # "translations_router",
]
