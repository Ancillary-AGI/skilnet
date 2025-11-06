"""
Enrollment management endpoints
"""

from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional, Dict, Any
from app.core.database import get_db
from app.api.v1.endpoints.auth import get_current_user
from app.models.user import User
from app.services.enrollment_service import EnrollmentService
from app.schemas.enrollment import (
    EnrollmentResponse, EnrollmentUpdate, EnrollmentStatistics,
    CertificateRequest, UserEnrollmentsResponse, CourseEnrollmentsResponse
)

router = APIRouter()

@router.get("/my-enrollments", response_model=UserEnrollmentsResponse)
async def get_user_enrollments(
    skip: int = Query(0, ge=0, description="Number of enrollments to skip"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of enrollments to return"),
    include_completed: bool = Query(True, description="Include completed enrollments"),
    include_active: bool = Query(True, description="Include active enrollments"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get current user's enrollments"""
    enrollment_service = EnrollmentService(db)
    result = await enrollment_service.get_user_enrollments(
        user_id=current_user.id,
        skip=skip,
        limit=limit,
        include_completed=include_completed,
        include_active=include_active
    )

    # Convert enrollments to response format
    enrollments_data = []
    completed_count = 0
    in_progress_count = 0

    for enrollment in result["enrollments"]:
        enrollment_dict = EnrollmentResponse.from_orm(enrollment)
        enrollments_data.append(enrollment_dict)

        if enrollment.is_completed:
            completed_count += 1
        elif enrollment.progress_percentage > 0:
            in_progress_count += 1

    return UserEnrollmentsResponse(
        enrollments=enrollments_data,
        total=result["total"],
        completed=completed_count,
        in_progress=in_progress_count
    )

@router.get("/{enrollment_id}", response_model=EnrollmentResponse)
async def get_enrollment(
    enrollment_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get enrollment by ID"""
    enrollment_service = EnrollmentService(db)

    # For now, allow users to see their own enrollments
    # In a more complex system, you might want different permission levels
    # TODO: Add proper permission checks

    # This endpoint would need to be modified to properly check ownership
    # For now, we'll implement a simpler version
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Individual enrollment retrieval not yet implemented"
    )

@router.put("/{enrollment_id}/progress", response_model=EnrollmentResponse)
async def update_enrollment_progress(
    enrollment_id: str,
    progress_data: EnrollmentUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update enrollment progress"""
    enrollment_service = EnrollmentService(db)

    # TODO: Implement proper enrollment ownership validation
    # For now, this is a placeholder
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Progress update not yet implemented"
    )

@router.post("/{enrollment_id}/complete", response_model=EnrollmentResponse)
async def complete_enrollment(
    enrollment_id: str,
    final_score: Optional[float] = Body(None, ge=0, le=100, description="Final assessment score"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Mark enrollment as completed"""
    enrollment_service = EnrollmentService(db)

    # TODO: Implement proper enrollment ownership validation and completion logic
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Enrollment completion not yet implemented"
    )

@router.delete("/{enrollment_id}")
async def unenroll_from_course(
    enrollment_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Unenroll from a course"""
    enrollment_service = EnrollmentService(db)

    # TODO: Implement unenrollment logic
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Unenrollment not yet implemented"
    )

@router.post("/{enrollment_id}/certificate", response_model=EnrollmentResponse)
async def issue_certificate(
    enrollment_id: str,
    certificate_data: CertificateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Issue completion certificate"""
    enrollment_service = EnrollmentService(db)

    # TODO: Implement certificate issuance logic
    raise HTTPException(
        status_code=status.HTTP_501_NOT_IMPLEMENTED,
        detail="Certificate issuance not yet implemented"
    )

@router.get("/course/{course_id}/enrollments")
async def get_course_enrollments(
    course_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get enrollments for a course (instructor only)"""
    # Check if user is instructor of the course
    from app.services.course_service import CourseService
    course_service = CourseService(db)
    course = await course_service.get_course_by_id(course_id)

    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )

    if course.instructor_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view course enrollments"
        )

    enrollment_service = EnrollmentService(db)
    result = await enrollment_service.get_course_enrollments(
        course_id=course_id,
        skip=skip,
        limit=limit
    )

    # Convert enrollments to response format
    enrollments_data = []
    for enrollment in result["enrollments"]:
        enrollments_data.append(EnrollmentResponse.from_orm(enrollment))

    # Get statistics
    statistics = await enrollment_service.get_enrollment_statistics(course_id)

    return CourseEnrollmentsResponse(
        enrollments=enrollments_data,
        total=result["total"],
        statistics=EnrollmentStatistics(**statistics)
    )

@router.get("/statistics/course/{course_id}")
async def get_course_enrollment_statistics(
    course_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get enrollment statistics for a course (instructor only)"""
    # Check if user is instructor of the course
    from app.services.course_service import CourseService
    course_service = CourseService(db)
    course = await course_service.get_course_by_id(course_id)

    if not course:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Course not found"
        )

    if course.instructor_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view course statistics"
        )

    enrollment_service = EnrollmentService(db)
    statistics = await enrollment_service.get_enrollment_statistics(course_id)

    return EnrollmentStatistics(**statistics)

@router.get("/statistics/global")
async def get_global_enrollment_statistics(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get global enrollment statistics (admin only)"""
    # TODO: Add admin check
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )

    enrollment_service = EnrollmentService(db)
    statistics = await enrollment_service.get_enrollment_statistics()

    return EnrollmentStatistics(**statistics)
