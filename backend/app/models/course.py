"""
Course and learning content models
"""

from sqlalchemy import Column, String, Text, Boolean, DateTime, Integer, Float, ForeignKey, JSON
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
from typing import List, Dict, Any, Optional
from enum import Enum

from app.core.database import Base


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


class Course(Base):
    """Course model with comprehensive features"""
    __tablename__ = "courses"
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title = Column(String(200), nullable=False, index=True)
    slug = Column(String(200), unique=True, index=True, nullable=False)
    description = Column(Text)
    short_description = Column(String(500))
    
    # Course metadata
    instructor_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    category = Column(String(100), index=True)
    subcategory = Column(String(100))
    tags = Column(ARRAY(String), default=list)
    language = Column(String(10), default="en")
    
    # Course properties
    difficulty_level = Column(String(20), default=DifficultyLevel.BEGINNER)
    estimated_duration_hours = Column(Float)
    price = Column(Float, default=0.0)
    currency = Column(String(3), default="USD")
    
    # Media and assets
    thumbnail_url = Column(String(500))
    trailer_video_url = Column(String(500))
    course_materials = Column(JSON, default=list)  # List of downloadable resources
    
    # VR/AR specific
    vr_environment_id = Column(String(100))  # Reference to VR environment
    ar_markers = Column(JSON, default=list)  # AR tracking markers
    spatial_audio_enabled = Column(Boolean, default=False)
    haptic_feedback_enabled = Column(Boolean, default=False)
    
    # AI Features
    ai_tutor_enabled = Column(Boolean, default=True)
    ai_difficulty_adaptation = Column(Boolean, default=True)
    ai_content_generation = Column(Boolean, default=False)
    
    # Course status and metrics
    is_published = Column(Boolean, default=False)
    is_featured = Column(Boolean, default=False)
    enrollment_count = Column(Integer, default=0)
    average_rating = Column(Float, default=0.0)
    total_reviews = Column(Integer, default=0)
    completion_rate = Column(Float, default=0.0)
    
    # Learning outcomes
    learning_objectives = Column(ARRAY(String), default=list)
    prerequisites = Column(ARRAY(String), default=list)
    skills_gained = Column(ARRAY(String), default=list)
    
    # Certification
    certificate_enabled = Column(Boolean, default=True)
    certificate_template_id = Column(String(100))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    published_at = Column(DateTime(timezone=True))
    
    # Relationships
    instructor = relationship("User", back_populates="taught_courses")
    modules = relationship("CourseModule", back_populates="course", cascade="all, delete-orphan")
    enrollments = relationship("Enrollment", back_populates="course")
    reviews = relationship("CourseReview", back_populates="course")
    
    def __repr__(self):
        return f"<Course(id={self.id}, title={self.title})>"
    
    @property
    def total_lessons(self) -> int:
        """Get total number of lessons in the course"""
        return sum(len(module.lessons) for module in self.modules)
    
    @property
    def total_duration_minutes(self) -> int:
        """Get total course duration in minutes"""
        return sum(
            lesson.duration_minutes or 0 
            for module in self.modules 
            for lesson in module.lessons
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert course to dictionary"""
        return {
            "id": str(self.id),
            "title": self.title,
            "slug": self.slug,
            "description": self.description,
            "short_description": self.short_description,
            "instructor_id": str(self.instructor_id),
            "category": self.category,
            "subcategory": self.subcategory,
            "tags": self.tags or [],
            "language": self.language,
            "difficulty_level": self.difficulty_level,
            "estimated_duration_hours": self.estimated_duration_hours,
            "price": self.price,
            "currency": self.currency,
            "thumbnail_url": self.thumbnail_url,
            "enrollment_count": self.enrollment_count,
            "average_rating": self.average_rating,
            "total_reviews": self.total_reviews,
            "is_published": self.is_published,
            "is_featured": self.is_featured,
            "learning_objectives": self.learning_objectives or [],
            "prerequisites": self.prerequisites or [],
            "skills_gained": self.skills_gained or [],
            "total_lessons": self.total_lessons,
            "total_duration_minutes": self.total_duration_minutes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "published_at": self.published_at.isoformat() if self.published_at else None,
        }


class CourseModule(Base):
    """Course module/chapter model"""
    __tablename__ = "course_modules"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    course_id = Column(UUID(as_uuid=True), ForeignKey("courses.id"), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    order_index = Column(Integer, nullable=False)
    
    # VR/AR specific
    vr_scene_id = Column(String(100))
    ar_content_id = Column(String(100))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    course = relationship("Course", back_populates="modules")
    lessons = relationship("Lesson", back_populates="module", cascade="all, delete-orphan")


class Lesson(Base):
    """Individual lesson model"""
    __tablename__ = "lessons"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    module_id = Column(UUID(as_uuid=True), ForeignKey("course_modules.id"), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text)
    content_type = Column(String(30), nullable=False)
    order_index = Column(Integer, nullable=False)
    
    # Content URLs and data
    video_url = Column(String(500))
    text_content = Column(Text)
    interactive_content = Column(JSON)  # For interactive elements
    
    # VR/AR Content
    vr_scene_url = Column(String(500))
    ar_model_url = Column(String(500))
    spatial_audio_url = Column(String(500))
    haptic_patterns = Column(JSON)
    
    # AI-Generated Content
    ai_generated = Column(Boolean, default=False)
    ai_model_version = Column(String(50))
    ai_generation_prompt = Column(Text)
    
    # Lesson properties
    duration_minutes = Column(Integer)
    is_free = Column(Boolean, default=False)
    requires_vr = Column(Boolean, default=False)
    requires_ar = Column(Boolean, default=False)
    
    # Assessment
    has_quiz = Column(Boolean, default=False)
    quiz_questions = Column(JSON, default=list)
    passing_score = Column(Float, default=70.0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    module = relationship("CourseModule", back_populates="lessons")
    progress = relationship("LessonProgress", back_populates="lesson")


class Enrollment(Base):
    """Course enrollment model"""
    __tablename__ = "enrollments"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    course_id = Column(UUID(as_uuid=True), ForeignKey("courses.id"), nullable=False)
    
    # Enrollment details
    enrolled_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
    progress_percentage = Column(Float, default=0.0)
    
    # Payment information
    payment_amount = Column(Float)
    payment_currency = Column(String(3))
    payment_method = Column(String(50))
    
    # Learning analytics
    total_time_spent_minutes = Column(Integer, default=0)
    last_accessed = Column(DateTime(timezone=True))
    completion_certificate_url = Column(String(500))
    
    # VR/AR usage
    vr_sessions_count = Column(Integer, default=0)
    ar_sessions_count = Column(Integer, default=0)
    total_vr_time_minutes = Column(Integer, default=0)
    
    # Relationships
    user = relationship("User")
    course = relationship("Course", back_populates="enrollments")
    lesson_progress = relationship("LessonProgress", back_populates="enrollment")


class LessonProgress(Base):
    """Individual lesson progress tracking"""
    __tablename__ = "lesson_progress"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    enrollment_id = Column(UUID(as_uuid=True), ForeignKey("enrollments.id"), nullable=False)
    lesson_id = Column(UUID(as_uuid=True), ForeignKey("lessons.id"), nullable=False)
    
    # Progress tracking
    is_completed = Column(Boolean, default=False)
    completion_percentage = Column(Float, default=0.0)
    time_spent_minutes = Column(Integer, default=0)
    
    # Assessment results
    quiz_score = Column(Float)
    quiz_attempts = Column(Integer, default=0)
    best_quiz_score = Column(Float)
    
    # VR/AR specific progress
    vr_interactions_count = Column(Integer, default=0)
    ar_objects_manipulated = Column(Integer, default=0)
    spatial_understanding_score = Column(Float)
    
    # AI interaction data
    ai_questions_asked = Column(Integer, default=0)
    ai_hints_used = Column(Integer, default=0)
    ai_feedback_rating = Column(Float)
    
    # Timestamps
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))
    last_accessed = Column(DateTime(timezone=True))
    
    # Relationships
    enrollment = relationship("Enrollment", back_populates="lesson_progress")
    lesson = relationship("Lesson", back_populates="progress")


class CourseReview(Base):
    """Course review and rating model"""
    __tablename__ = "course_reviews"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    course_id = Column(UUID(as_uuid=True), ForeignKey("courses.id"), nullable=False)
    
    # Review content
    rating = Column(Float, nullable=False)  # 1-5 stars
    title = Column(String(200))
    content = Column(Text)
    
    # Detailed ratings
    content_quality_rating = Column(Float)
    instructor_rating = Column(Float)
    value_for_money_rating = Column(Float)
    vr_experience_rating = Column(Float)
    ai_tutor_rating = Column(Float)
    
    # Review metadata
    is_verified_purchase = Column(Boolean, default=False)
    helpful_votes = Column(Integer, default=0)
    total_votes = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    user = relationship("User")
    course = relationship("Course", back_populates="reviews")