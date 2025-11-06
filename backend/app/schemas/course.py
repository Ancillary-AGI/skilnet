"""
Course schemas for EduVerse platform
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum


class CourseDifficulty(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"


class CourseFilter(BaseModel):
    """Course filtering options"""
    category_id: Optional[str] = None
    difficulty_level: Optional[str] = None
    instructor_id: Optional[str] = None
    is_free: Optional[bool] = None
    supports_vr: Optional[bool] = None
    supports_ar: Optional[bool] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    search_query: Optional[str] = None
    sort_by: Optional[str] = "created_at"
    sort_order: Optional[str] = "desc"


class CourseBase(BaseModel):
    """Base course schema"""
    title: str = Field(..., min_length=1, max_length=200, description="Course title")
    description: Optional[str] = Field(None, description="Detailed course description")
    short_description: Optional[str] = Field(None, max_length=500, description="Brief course description")
    thumbnail_url: Optional[str] = Field(None, description="Course thumbnail image URL")
    trailer_video_url: Optional[str] = Field(None, description="Trailer video URL")
    duration_minutes: int = Field(0, ge=0, description="Course duration in minutes")
    difficulty_level: str = Field("beginner", description="Course difficulty level")
    category_id: Optional[str] = Field(None, description="Category ID")
    price: float = Field(0.0, ge=0, description="Course price")
    currency: str = Field("USD", description="Currency code")
    is_free: bool = Field(True, description="Whether course is free")
    supports_vr: bool = Field(False, description="VR support")
    supports_ar: bool = Field(False, description="AR support")
    vr_environment_url: Optional[str] = Field(None, description="VR environment URL")
    ar_markers: Optional[List[Dict[str, Any]]] = Field(None, description="AR markers data")
    tags: Optional[List[str]] = Field(None, description="Course tags")
    learning_objectives: Optional[List[str]] = Field(None, description="Learning objectives")
    prerequisites: Optional[List[str]] = Field(None, description="Course prerequisites")
    ai_generated_content: bool = Field(False, description="AI generated content flag")
    personalization_enabled: bool = Field(True, description="Personalization enabled")


class CourseCreate(CourseBase):
    """Schema for creating a new course"""
    pass


class CourseUpdate(BaseModel):
    """Schema for updating a course"""
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = None
    short_description: Optional[str] = Field(None, max_length=500)
    thumbnail_url: Optional[str] = None
    trailer_video_url: Optional[str] = None
    duration_minutes: Optional[int] = Field(None, ge=0)
    difficulty_level: Optional[str] = None
    category_id: Optional[str] = None
    price: Optional[float] = Field(None, ge=0)
    currency: Optional[str] = None
    is_free: Optional[bool] = None
    supports_vr: Optional[bool] = None
    supports_ar: Optional[bool] = None
    vr_environment_url: Optional[str] = None
    ar_markers: Optional[List[Dict[str, Any]]] = None
    tags: Optional[List[str]] = None
    learning_objectives: Optional[List[str]] = None
    prerequisites: Optional[List[str]] = None
    ai_generated_content: Optional[bool] = None
    personalization_enabled: Optional[bool] = None


class CourseResponse(CourseBase):
    """Schema for course response"""
    id: str = Field(..., description="Course ID")
    slug: str = Field(..., description="URL-friendly course slug")
    instructor_id: str = Field(..., description="Instructor ID")
    is_published: bool = Field(False, description="Publication status")
    is_featured: bool = Field(False, description="Featured status")
    enrollment_count: int = Field(0, description="Number of enrollments")
    completion_rate: float = Field(0.0, description="Completion rate percentage")
    average_rating: float = Field(0.0, description="Average rating")
    total_ratings: int = Field(0, description="Total number of ratings")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    published_at: Optional[datetime] = Field(None, description="Publication timestamp")

    class Config:
        from_attributes = True


class CourseDetailResponse(CourseResponse):
    """Detailed course response with related data"""
    instructor: Optional[Dict[str, Any]] = Field(None, description="Instructor information")
    category: Optional[Dict[str, Any]] = Field(None, description="Category information")

    class Config:
        from_attributes = True


# Enrollment schemas
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
    progress_percentage: Optional[float] = Field(None, ge=0, le=100)
    is_completed: Optional[bool] = None


class EnrollmentResponse(EnrollmentBase):
    """Enrollment response schema"""
    id: str = Field(..., description="Enrollment ID")
    user_id: str = Field(..., description="User ID")
    enrolled_at: datetime = Field(..., description="Enrollment timestamp")
    completed_at: Optional[datetime] = Field(None, description="Completion timestamp")
    last_accessed_at: Optional[datetime] = Field(None, description="Last access timestamp")

    class Config:
        from_attributes = True


# Rating/Review schemas
class CourseRatingBase(BaseModel):
    """Base course rating schema"""
    rating: float = Field(..., ge=1.0, le=5.0, description="Rating value (1-5)")
    review_text: Optional[str] = Field(None, max_length=1000, description="Review text")


class CourseRatingCreate(CourseRatingBase):
    """Schema for creating course rating"""
    pass


class CourseRatingUpdate(BaseModel):
    """Schema for updating course rating"""
    rating: Optional[float] = Field(None, ge=1.0, le=5.0)
    review_text: Optional[str] = Field(None, max_length=1000)


class CourseRatingResponse(CourseRatingBase):
    """Course rating response schema"""
    id: str = Field(..., description="Rating ID")
    user_id: str = Field(..., description="User ID")
    course_id: str = Field(..., description="Course ID")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Update timestamp")

    class Config:
        from_attributes = True


# Statistics schemas
class CourseStatistics(BaseModel):
    """Course statistics schema"""
    total_enrollments: int = Field(0, description="Total enrollments")
    active_enrollments: int = Field(0, description="Active enrollments")
    completion_rate: float = Field(0.0, description="Completion rate percentage")
    average_rating: float = Field(0.0, description="Average rating")
    total_ratings: int = Field(0, description="Total ratings")
    total_revenue: float = Field(0.0, description="Total revenue")
    monthly_enrollments: List[Dict[str, Any]] = Field([], description="Monthly enrollment data")


# Instructor dashboard schemas
class InstructorCourseSummary(BaseModel):
    """Summary for instructor's courses"""
    course_id: str
    course_title: str
    enrollment_count: int
    average_rating: float
    total_ratings: int
    total_revenue: float
    is_published: bool
    created_at: datetime
