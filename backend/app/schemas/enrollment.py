"""
Enrollment schemas for EduVerse platform
"""

from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class EnrollmentBase(BaseModel):
    """Base enrollment schema"""
    course_id: str = Field(..., description="Course ID")
    progress_percentage: float = Field(0.0, ge=0, le=100, description="Progress percentage")
    is_completed: bool = Field(False, description="Completion status")


class EnrollmentCreate(EnrollmentBase):
    """Schema for creating enrollment"""
    pass


class EnrollmentUpdate(BaseModel):
    """Schema for updating enrollment"""
    progress_percentage: Optional[float] = Field(None, ge=0, le=100, description="Progress percentage")
    quiz_score: Optional[float] = Field(None, ge=0, le=100, description="Quiz score")
    final_score: Optional[float] = Field(None, ge=0, le=100, description="Final assessment score")
    time_spent_minutes: Optional[int] = Field(None, ge=0, description="Time spent in minutes")


class EnrollmentResponse(EnrollmentBase):
    """Enrollment response schema"""
    id: str = Field(..., description="Enrollment ID")
    user_id: str = Field(..., description="User ID")
    enrolled_at: datetime = Field(..., description="Enrollment timestamp")
    completed_at: Optional[datetime] = Field(None, description="Completion timestamp")
    last_accessed_at: Optional[datetime] = Field(None, description="Last access timestamp")
    time_spent_minutes: int = Field(0, description="Total time spent in minutes")
    lessons_completed: int = Field(0, description="Lessons completed")
    total_lessons: int = Field(0, description="Total lessons")
    quiz_score: Optional[float] = Field(None, description="Average quiz score")
    final_score: Optional[float] = Field(None, description="Final assessment score")
    certificate_issued: bool = Field(False, description="Certificate issued status")
    certificate_url: Optional[str] = Field(None, description="Certificate URL")
    grade: Optional[str] = Field(None, description="Letter grade")
    status: str = Field(..., description="Enrollment status")

    class Config:
        from_attributes = True


class EnrollmentDetailResponse(EnrollmentResponse):
    """Detailed enrollment response with related data"""
    course: Optional[Dict[str, Any]] = Field(None, description="Course information")
    user: Optional[Dict[str, Any]] = Field(None, description="User information")

    class Config:
        from_attributes = True


class EnrollmentProgressUpdate(BaseModel):
    """Schema for progress updates"""
    progress_percentage: float = Field(..., ge=0, le=100, description="New progress percentage")
    lesson_completed: bool = Field(False, description="Whether a lesson was completed")
    time_spent: int = Field(0, ge=0, description="Time spent in this session (minutes)")


class EnrollmentStatistics(BaseModel):
    """Enrollment statistics schema"""
    total_enrollments: int = Field(0, description="Total enrollments")
    active_enrollments: int = Field(0, description="Active enrollments")
    completed_enrollments: int = Field(0, description="Completed enrollments")
    average_progress: float = Field(0.0, description="Average progress percentage")
    average_final_score: float = Field(0.0, description="Average final score")
    completion_rate: float = Field(0.0, description="Completion rate percentage")
    average_time_spent: int = Field(0, description="Average time spent (minutes)")


class CertificateRequest(BaseModel):
    """Certificate request schema"""
    certificate_url: str = Field(..., description="URL of the issued certificate")


class UserEnrollmentsResponse(BaseModel):
    """Response for user's enrollments"""
    enrollments: list[EnrollmentResponse] = Field([], description="List of enrollments")
    total: int = Field(0, description="Total number of enrollments")
    completed: int = Field(0, description="Number of completed enrollments")
    in_progress: int = Field(0, description="Number of enrollments in progress")

    class Config:
        from_attributes = True


class CourseEnrollmentsResponse(BaseModel):
    """Response for course enrollments"""
    enrollments: list[EnrollmentDetailResponse] = Field([], description="List of enrollments")
    total: int = Field(0, description="Total number of enrollments")
    statistics: EnrollmentStatistics = Field(..., description="Enrollment statistics")

    class Config:
        from_attributes = True
