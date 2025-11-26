"""
Course management endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any
from app.core.database import get_db
from app.api.v1.endpoints.auth import get_current_user
from app.models.user import User
from app.services.course_service import CourseService
from app.services.enrollment_service import EnrollmentService
from app.schemas.course import CourseCreate, CourseUpdate, CourseFilter, CourseResponse, CourseRatingCreate, CourseRatingResponse
from app.schemas.enrollment import EnrollmentResponse, EnrollmentUpdate

router = APIRouter()

@router.get("/", response_model=Dict[str, Any])
async def get_courses(
    skip: int = Query(0, ge=0, description="Number of courses to skip"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of courses to return"),
    category_id: Optional[str] = Query(None, description="Filter by category ID"),
    difficulty_level: Optional[str] = Query(None, description="Filter by difficulty level"),
    instructor_id: Optional[str] = Query(None, description="Filter by instructor ID"),
    is_free: Optional[bool] = Query(None, description="Filter by free courses"),
    supports_vr: Optional[bool] = Query(None, description="Filter by VR support"),
    supports_ar: Optional[bool] = Query(None, description="Filter by AR support"),
    min_price: Optional[float] = Query(None, ge=0, description="Minimum price filter"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum price filter"),
    search_query: Optional[str] = Query(None, description="Search in title and description"),
    sort_by: Optional[str] = Query("created_at", description="Sort field"),
    sort_order: Optional[str] = Query("desc", description="Sort order (asc/desc)"),
    db: AsyncSession = Depends(get_db)
):
    """Get list of courses with filtering and pagination"""
    course_service = CourseService(db)

    # Build filters
    filters = CourseFilter(
        category_id=category_id,
        difficulty_level=difficulty_level,
        instructor_id=instructor_id,
        is_free=is_free,
        supports_vr=supports_vr,
        supports_ar=supports_ar,
        min_price=min_price,
        max_price=max_price,
        search_query=search_query,
        sort_by=sort_by,
        sort_order=sort_order
    )

    result = await course_service.get_courses(skip=skip, limit=limit, filters=filters)

    # Convert courses to response format
    courses_data = []
    for course in result["courses"]:
        courses_data.append(CourseResponse.from_orm(course))

    return {
        "courses": courses_data,
        "total": result["total"],
        "skip": result["skip"],
        "limit": result["limit"]
    }

@router.get("/{course_id}", response_model=CourseResponse)
async def get_course(
    course_id: str,
    db: AsyncSession = Depends(get_db)
):
    """Get course by ID"""
    course_service = CourseService(db)
    course = await course_service.get_course_by_id(course_id)

    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )

    return CourseResponse.from_orm(course)

@router.get("/slug/{slug}", response_model=CourseResponse)
async def get_course_by_slug(
    slug: str,
    db: AsyncSession = Depends(get_db)
):
    """Get course by slug"""
    course_service = CourseService(db)
    course = await course_service.get_course_by_slug(slug)

    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )

    return CourseResponse.from_orm(course)

@router.post("/", response_model=CourseResponse)
async def create_course(
    course_data: CourseCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new course (instructors only)"""
    # Check if user is an instructor
    if not current_user.is_instructor:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only instructors can create courses"
        )

    course_service = CourseService(db)
    course = await course_service.create_course(course_data, current_user.id)

    return CourseResponse.from_orm(course)

@router.put("/{course_id}", response_model=CourseResponse)
async def update_course(
    course_id: str,
    course_data: CourseUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update course (instructor only)"""
    course_service = CourseService(db)
    course = await course_service.update_course(course_id, course_data, current_user.id)

    return CourseResponse.from_orm(course)

@router.delete("/{course_id}")
async def delete_course(
    course_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete course (instructor only)"""
    course_service = CourseService(db)
    success = await course_service.delete_course(course_id, current_user.id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to delete course"
        )

    return {"message": "Course deleted successfully"}

@router.post("/{course_id}/publish", response_model=CourseResponse)
async def publish_course(
    course_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Publish course (instructor only)"""
    course_service = CourseService(db)
    course = await course_service.publish_course(course_id, current_user.id)

    return CourseResponse.from_orm(course)

@router.post("/{course_id}/enroll", response_model=EnrollmentResponse)
async def enroll_in_course(
    course_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Enroll user in course"""
    enrollment_service = EnrollmentService(db)
    enrollment = await enrollment_service.enroll_user_in_course(current_user.id, course_id)

    return EnrollmentResponse.from_orm(enrollment)

@router.get("/instructor/my-courses")
async def get_instructor_courses(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    include_unpublished: bool = Query(False, description="Include unpublished courses"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get courses created by current instructor"""
    course_service = CourseService(db)

    filters = CourseFilter(instructor_id=current_user.id)
    result = await course_service.get_courses(
        skip=skip,
        limit=limit,
        filters=filters,
        include_unpublished=include_unpublished
    )

    # Convert courses to response format
    courses_data = []
    for course in result["courses"]:
        courses_data.append(CourseResponse.from_orm(course))

    return {
        "courses": courses_data,
        "total": result["total"],
        "skip": result["skip"],
        "limit": result["limit"]
    }

@router.post("/{course_id}/rate")
async def rate_course(
    course_id: str,
    rating_data: CourseRatingCreate = Body(...),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Rate a course"""
    course_service = CourseService(db)

    # Check if course exists
    course = await course_service.get_course_by_id(course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )

    # Create or update rating
    rating = await course_service.create_or_update_rating(
        current_user.id, course_id, rating_data
    )

    return {
        "message": "Course rated successfully",
        "course_id": course_id,
        "rating": rating.rating,
        "review_text": rating.review_text
    }

@router.get("/{course_id}/ratings")
async def get_course_ratings(
    course_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db)
):
    """Get ratings for a course"""
    course_service = CourseService(db)

    # Check if course exists
    course = await course_service.get_course_by_id(course_id)
    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )

    result = await course_service.get_course_ratings(course_id, skip=skip, limit=limit)

    # Convert ratings to response format
    ratings_data = []
    for rating in result["ratings"]:
        ratings_data.append(CourseRatingResponse.from_orm(rating))

    return {
        "course_id": course_id,
        "ratings": ratings_data,
        "total": result["total"],
        "skip": result["skip"],
        "limit": result["limit"]
    }

@router.delete("/{course_id}/rating")
async def delete_course_rating(
    course_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete user's rating for a course"""
    course_service = CourseService(db)

    success = await course_service.delete_rating(current_user.id, course_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Rating not found"
        )

    return {"message": "Rating deleted successfully"}
