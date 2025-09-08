import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
from sqlmodel import SQLModel, Field

class DifficultyLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

class ContentType(str, Enum):
    VIDEO = "video"
    TEXT = "text"
    INTERACTIVE = "interactive"
    VR_EXPERIENCE = "vr_experience"
    AR_EXPERIENCE = "ar_experience"
    AI_SIMULATION = "ai_simulation"
    QUIZ = "quiz"
    ASSIGNMENT = "assignment"
    LIVE_CLASS = "live_class"
    PODCAST = "podcast"
    CODE_EXERCISE = "code_exercise"
    WHITEBOARD = "whiteboard"

class CourseStatus(str, Enum):
    DRAFT = "draft"
    PUBLISHED = "published"
    ARCHIVED = "archived"
    UNDER_REVIEW = "under_review"

class Course(SQLModel, table=True):
    __tablename__ = "courses"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    title: str = Field(nullable=False)
    slug: str = Field(unique=True, index=True, nullable=False)
    description: Optional[str] = Field(default=None)
    short_description: Optional[str] = Field(default=None)
    instructor_id: str = Field(index=True, nullable=False)
    category: Optional[str] = Field(default=None, index=True)
    subcategory: Optional[str] = Field(default=None, index=True)
    tags: List[str] = Field(default_factory=list)
    language: str = Field(default="en")
    difficulty_level: str = Field(default=DifficultyLevel.BEGINNER.value)
    estimated_duration_hours: float = Field(default=0.0)
    price: float = Field(default=0.0)
    currency: str = Field(default='USD')
    thumbnail_url: Optional[str] = Field(default=None)
    trailer_video_url: Optional[str] = Field(default=None)
    course_materials: List[Dict[str, Any]] = Field(default_factory=list)
    vr_environment_id: Optional[str] = Field(default=None)
    ar_markers: List[Dict[str, Any]] = Field(default_factory=list)
    spatial_audio_enabled: bool = Field(default=False)
    haptic_feedback_enabled: bool = Field(default=False)
    ai_tutor_enabled: bool = Field(default=False)
    ai_difficulty_adaptation: bool = Field(default=False)
    ai_content_generation: bool = Field(default=False)
    status: str = Field(default=CourseStatus.DRAFT.value)
    is_featured: bool = Field(default=False)
    enrollment_count: int = Field(default=0)
    average_rating: float = Field(default=0.0)
    total_reviews: int = Field(default=0)
    completion_rate: float = Field(default=0.0)
    learning_objectives: List[str] = Field(default_factory=list)
    prerequisites: List[str] = Field(default_factory=list)
    skills_gained: List[str] = Field(default_factory=list)
    certificate_enabled: bool = Field(default=False)
    certificate_template_id: Optional[str] = Field(default=None)
    ar_content_id: Optional[str] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    published_at: Optional[datetime] = Field(default=None)

class Module(SQLModel, table=True):
    """Course modules for organizing lessons"""
    __tablename__ = "modules"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    course_id: str = Field(index=True, nullable=False)
    title: str = Field(nullable=False)
    description: Optional[str] = Field(default=None)
    order_index: int = Field(nullable=False)
    is_free: bool = Field(default=False)
    estimated_duration_hours: float = Field(default=0.0)
    learning_objectives: List[str] = Field(default_factory=list)
    prerequisites: List[str] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class Lesson(SQLModel, table=True):
    """Individual lessons within modules"""
    __tablename__ = "lessons"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    module_id: str = Field(index=True, nullable=False)
    course_id: str = Field(index=True, nullable=False)
    title: str = Field(nullable=False)
    description: Optional[str] = Field(default=None)
    content_type: str = Field(nullable=False)
    order_index: int = Field(nullable=False)

    # Content URLs
    video_url: Optional[str] = Field(default=None)
    text_content: Optional[str] = Field(default=None)
    interactive_content: Optional[Dict[str, Any]] = Field(default=None)
    vr_scene_url: Optional[str] = Field(default=None)
    ar_model_url: Optional[str] = Field(default=None)
    spatial_audio_url: Optional[str] = Field(default=None)

    # VR/AR Features
    haptic_patterns: List[Dict[str, Any]] = Field(default_factory=list)
    hand_tracking_data: Optional[Dict[str, Any]] = Field(default=None)
    spatial_coordinates: Optional[Dict[str, Any]] = Field(default=None)

    # AI Features
    ai_generated: bool = Field(default=False)
    ai_model_version: Optional[str] = Field(default=None)
    ai_generation_prompt: Optional[str] = Field(default=None)
    ai_difficulty_level: Optional[str] = Field(default=None)
    ai_adaptive_content: Optional[Dict[str, Any]] = Field(default=None)

    # Learning Features
    duration_minutes: Optional[int] = Field(default=None)
    is_free: bool = Field(default=False)
    requires_vr: bool = Field(default=False)
    requires_ar: bool = Field(default=False)
    has_quiz: bool = Field(default=False)
    quiz_questions: List[Dict[str, Any]] = Field(default_factory=list)
    passing_score: float = Field(default=70.0)

    # Gamification
    points_value: int = Field(default=10)
    badges_available: List[str] = Field(default_factory=list)

    # Offline Support
    downloadable: bool = Field(default=True)
    file_size_mb: Optional[float] = Field(default=None)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class Enrollment(SQLModel, table=True):
    """User course enrollments with progress tracking"""
    __tablename__ = "enrollments"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    user_id: str = Field(index=True, nullable=False)
    course_id: str = Field(index=True, nullable=False)
    enrolled_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = Field(default=None)
    progress_percentage: float = Field(default=0.0)

    # Payment Information
    payment_amount: float = Field(default=0.0)
    payment_currency: Optional[str] = Field(default=None)
    payment_method: Optional[str] = Field(default=None)
    payment_status: str = Field(default="completed")

    # Learning Progress
    total_time_spent_minutes: int = Field(default=0)
    last_accessed: Optional[datetime] = Field(default=None)
    completion_certificate_url: Optional[str] = Field(default=None)

    # VR/AR Sessions
    vr_sessions_count: int = Field(default=0)
    ar_sessions_count: int = Field(default=0)
    total_vr_time_minutes: int = Field(default=0)
    total_ar_time_minutes: int = Field(default=0)

    # AI Learning Analytics
    ai_recommendations_used: int = Field(default=0)
    ai_hints_requested: int = Field(default=0)
    ai_adaptive_difficulty_changes: int = Field(default=0)

    # Learning Style Adaptation
    preferred_learning_style: Optional[str] = Field(default=None)
    adaptive_pace_enabled: bool = Field(default=True)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class LessonProgress(SQLModel, table=True):
    """Detailed progress tracking for individual lessons"""
    __tablename__ = "lesson_progress"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    enrollment_id: str = Field(index=True, nullable=False)
    lesson_id: str = Field(index=True, nullable=False)
    user_id: str = Field(index=True, nullable=False)

    # Completion Status
    is_completed: bool = Field(default=False)
    completion_percentage: float = Field(default=0.0)
    time_spent_minutes: int = Field(default=0)

    # Quiz Performance
    quiz_score: Optional[float] = Field(default=None)
    quiz_attempts: int = Field(default=0)
    best_quiz_score: Optional[float] = Field(default=None)
    last_quiz_attempt: Optional[datetime] = Field(default=None)

    # VR/AR Interactions
    vr_interactions_count: int = Field(default=0)
    ar_objects_manipulated: int = Field(default=0)
    spatial_understanding_score: Optional[float] = Field(default=None)
    hand_tracking_accuracy: Optional[float] = Field(default=None)

    # AI Learning Analytics
    ai_questions_asked: int = Field(default=0)
    ai_hints_used: int = Field(default=0)
    ai_feedback_rating: Optional[float] = Field(default=None)
    ai_adaptive_hints: List[Dict[str, Any]] = Field(default_factory=list)

    # Learning Analytics
    learning_style_detected: Optional[str] = Field(default=None)
    attention_span_minutes: Optional[int] = Field(default=None)
    engagement_score: Optional[float] = Field(default=None)

    # Timestamps
    started_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = Field(default=None)
    last_accessed: Optional[datetime] = Field(default=None)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class CourseReview(SQLModel, table=True):
    """User reviews and ratings for courses"""
    __tablename__ = "course_reviews"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    user_id: str = Field(index=True, nullable=False)
    course_id: str = Field(index=True, nullable=False)

    # Overall Rating
    rating: float = Field(default=0.0)
    title: Optional[str] = Field(default=None)
    content: Optional[str] = Field(default=None)

    # Detailed Ratings
    content_quality_rating: Optional[float] = Field(default=None)
    instructor_rating: Optional[float] = Field(default=None)
    value_for_money_rating: Optional[float] = Field(default=None)
    vr_experience_rating: Optional[float] = Field(default=None)
    ar_experience_rating: Optional[float] = Field(default=None)
    ai_tutor_rating: Optional[float] = Field(default=None)
    difficulty_appropriateness: Optional[float] = Field(default=None)

    # Review Metadata
    is_verified_purchase: bool = Field(default=False)
    helpful_votes: int = Field(default=0)
    total_votes: int = Field(default=0)
    reported_count: int = Field(default=0)

    # Learning Context
    completed_course: bool = Field(default=False)
    time_since_completion_days: Optional[int] = Field(default=None)
    learning_style_feedback: Optional[str] = Field(default=None)

    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
