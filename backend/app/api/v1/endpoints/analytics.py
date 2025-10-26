"""
Analytics endpoints
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.api.v1.endpoints.auth import get_current_user
from app.models.user import User

router = APIRouter()

@router.get("/dashboard")
async def get_analytics_dashboard(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get user analytics dashboard"""
    return {
        "total_courses": 0,
        "completed_courses": 0,
        "total_hours": 0,
        "current_streak": current_user.current_streak,
        "total_xp": current_user.total_xp,
        "level": current_user.current_level
    }