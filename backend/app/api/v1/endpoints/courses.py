"""
Course management endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from app.core.database import get_db
from app.api.v1.endpoints.auth import get_current_user
from app.models.user import User

router = APIRouter()

@router.get("/")
async def get_courses(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    category: Optional[str] = None,
    difficulty: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """Get list of courses"""
    return {
        "courses": [],
        "total": 0,
        "skip": skip,
        "limit": limit
    }

@router.get("/{course_id}")
async def get_course(
    course_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get course by ID"""
    return {
        "id": course_id,
        "title": "Sample Course",
        "description": "Course description",
        "status": "active"
    }

@router.post("/{course_id}/enroll")
async def enroll_in_course(
    course_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Enroll user in course"""
    return {
        "message": "Successfully enrolled in course",
        "course_id": course_id,
        "user_id": current_user.id
    }