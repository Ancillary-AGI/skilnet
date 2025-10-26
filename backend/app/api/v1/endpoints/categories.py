"""
Category endpoints
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db

router = APIRouter()

@router.get("/")
async def get_categories(
    db: AsyncSession = Depends(get_db)
):
    """Get all course categories"""
    return {
        "categories": [
            {"id": "tech", "name": "Technology", "icon": "💻"},
            {"id": "business", "name": "Business", "icon": "💼"},
            {"id": "design", "name": "Design", "icon": "🎨"},
            {"id": "science", "name": "Science", "icon": "🔬"},
            {"id": "language", "name": "Languages", "icon": "🌍"},
        ]
    }