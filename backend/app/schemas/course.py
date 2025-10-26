from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from uuid import UUID

# Category schemas
class CategoryBase(BaseModel):
    name: str
    slug: str
    description: Optional[str] = None
    parent_id: Optional[UUID] = None
    is_active: bool = True
    sort_order: int = 0
    icon_url: Optional[str] = None
    color_code: str = "#3B82F6"

class CategoryCreate(CategoryBase):
    pass

class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    parent_id: Optional[UUID] = None
    is_active: Optional[bool] = None
    sort_order: Optional[int] = None
    icon_url: Optional[str] = None
    color_code: Optional[str] = None

class CategoryResponse(CategoryBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# Course schemas
class CourseBase(BaseModel):
    title: str
    slug: str
    description: Optional[str] = None
    short_description: Optional[str] = None
    category_id: Optional[UUID] = None
    instructor_id: UUID

    difficulty: str = "beginner"
    status: str = "draft"
    price: float = 0.0
    currency: str = "USD"

    thumbnail_url: Optional[str] = None
    video_url: Optional[str] = None
    duration_hours: float = 0.0

    is_featured: bool = False
    is_free: bool = True
    has_certificate: bool = False
    prerequisites: List[str] = []
    learning_objectives: List[str] = []
    tags: List[str] = []

class CourseCreate(CourseBase):
    pass

class CourseUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    short_description: Optional[str] = None
    category_id: Optional[UUID] = None
    difficulty: Optional[str] = None
    status: Optional[str] = None
    price: Optional[float] = None
    currency: Optional[str] = None
    thumbnail_url: Optional[str] = None
    video_url: Optional[str] = None
    duration_hours: Optional[float] = None
    is_featured: Optional[bool] = None
    is_free: Optional[bool] = None
    has_certificate: Optional[bool] = None
    prerequisites: Optional[List[str]] = None
    learning_objectives: Optional[List[str]] = None
    tags: Optional[List[str]] = None

class CourseResponse(CourseBase):
    id: UUID
    enrollment_count: int
    rating: float
    review_count: int
    created_at: datetime
    updated_at: datetime
    published_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class CourseWithDetailsResponse(CourseResponse):
    category: Optional[CategoryResponse] = None
    instructor_name: str

    class Config:
        from_attributes = True

# Enrollment schemas
class EnrollmentBase(BaseModel):
    user_id: UUID
    course_id: UUID
    progress_percentage: float = 0.0
    is_completed: bool = False
    completed_at: Optional[datetime] = None

class EnrollmentCreate(EnrollmentBase):
    pass

class EnrollmentUpdate(BaseModel):
    progress_percentage: Optional[float] = None
    is_completed: Optional[bool] = None

class EnrollmentResponse(EnrollmentBase):
    id: UUID
    enrolled_at: datetime
    last_accessed_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# Review schemas
class CourseReviewBase(BaseModel):
    user_id: UUID
    course_id: UUID
    rating: int = Field(..., ge=1, le=5)
    review_text: Optional[str] = None
    is_recommended: bool = True

class CourseReviewCreate(CourseReviewBase):
    pass

class CourseReviewUpdate(BaseModel):
    rating: Optional[int] = Field(None, ge=1, le=5)
    review_text: Optional[str] = None
    is_recommended: Optional[bool] = None

class CourseReviewResponse(CourseReviewBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
