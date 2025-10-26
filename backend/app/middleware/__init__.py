"""
Middleware module for EduVerse platform
"""

# I18n middleware for internationalization
from .i18n_middleware import I18nMiddleware

__all__ = [
    "I18nMiddleware",
]
