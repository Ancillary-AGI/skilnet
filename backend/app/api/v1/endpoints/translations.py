"""
Translation endpoints
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db

router = APIRouter()

@router.get("/{language}")
async def get_translations(
    language: str,
    db: AsyncSession = Depends(get_db)
):
    """Get translations for specified language"""
    return {
        "language": language,
        "translations": {
            "welcome": "Welcome",
            "login": "Login",
            "register": "Register",
            "courses": "Courses",
            "profile": "Profile"
        }
    }