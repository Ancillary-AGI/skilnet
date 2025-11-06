"""
Course model for EduVerse platform
"""

from sqlalchemy import Column, String, Text, Boolean, DateTime, Integer, Float, JSON, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime
from typing import Dict, Any, List
import uuid

class Course(Base):
    __tablename__ = "courses"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    title = Column(String, nullable=False, index=True)
    slug = Column(String, unique=True, index=True)
    description = Column(Text)
    short_description = Column(String(500))
    
    # Content
    thumbnail_url = Column(String)
    trailer_video_url = Column(String)
    duration_minutes = Column(Integer, default=0)
    difficulty_level = Column(String, default="beginner")  # beginner, intermediate, advanced
    
    # Instructor
    instructor_id = Column(String, ForeignKey("users.id"))
    instructor = relationship("User", back_populates="courses")

    # Category
    category_id = Column(String, ForeignKey("categories.id"))
    category = relationship("Category", back_populates="courses")

    # Relationships
    enrollments = relationship("Enrollment", back_populates="course")

    # Pricing
    price = Column(Float, default=0.0)
    currency = Column(String, default="USD")
    is_free = Column(Boolean, default=False)
    
    # Status
    is_published = Column(Boolean, default=False)
    is_featured = Column(Boolean, default=False)
    
    # Metadata
    tags = Column(JSON)  # List of tags
    learning_objectives = Column(JSON)  # List of learning objectives
    prerequisites = Column(JSON)  # List of prerequisites
    
    # VR/AR specific
    supports_vr = Column(Boolean, default=False)
    supports_ar = Column(Boolean, default=False)
    vr_environment_url = Column(String)
    ar_markers = Column(JSON)
    
    # AI features
    ai_generated_content = Column(Boolean, default=False)
    personalization_enabled = Column(Boolean, default=True)
    
    # Statistics
    enrollment_count = Column(Integer, default=0)
    completion_rate = Column(Float, default=0.0)
    average_rating = Column(Float, default=0.0)
    total_ratings = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    published_at = Column(DateTime)
    
    def __repr__(self):
        return f"<Course(id={self.id}, title={self.title})>"
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "title": self.title,
            "slug": self.slug,
            "description": self.description,
            "short_description": self.short_description,
            "thumbnail_url": self.thumbnail_url,
            "duration_minutes": self.duration_minutes,
            "difficulty_level": self.difficulty_level,
            "price": self.price,
            "currency": self.currency,
            "is_free": self.is_free,
            "is_published": self.is_published,
            "supports_vr": self.supports_vr,
            "supports_ar": self.supports_ar,
            "enrollment_count": self.enrollment_count,
            "average_rating": self.average_rating,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
