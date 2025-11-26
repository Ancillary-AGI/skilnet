"""
Course rating model for EduVerse platform

This module defines the CourseRating SQLAlchemy model which represents
individual user ratings and reviews for courses in the EduVerse platform.
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime
from typing import Optional
import uuid


class CourseRating(Base):
    """
    Course rating model representing individual user ratings for courses.

    This model stores detailed rating information including star ratings,
    review text, and timestamps for course quality assessment.

    Attributes:
        id: Unique identifier for the rating
        user_id: ID of the user who gave the rating
        course_id: ID of the course being rated
        rating: Star rating (1-5)
        review_text: Optional detailed review text
        created_at: When the rating was created
        updated_at: When the rating was last updated

    Relationships:
        user: The user who gave the rating
        course: The course being rated
    """

    __tablename__ = "course_ratings"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    course_id = Column(String, ForeignKey("courses.id", ondelete="CASCADE"), nullable=False, index=True)

    # Rating data
    rating = Column(Float, nullable=False)  # 1.0 to 5.0
    review_text = Column(Text, nullable=True)

    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="course_ratings")
    course = relationship("Course", back_populates="ratings")

    # Ensure one rating per user per course
    __table_args__ = (
        UniqueConstraint('user_id', 'course_id', name='unique_user_course_rating'),
    )

    def __repr__(self):
        return f"<CourseRating(user_id={self.user_id}, course_id={self.course_id}, rating={self.rating})>"

    def to_dict(self) -> dict:
        """Convert rating to dictionary"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "course_id": self.course_id,
            "rating": self.rating,
            "review_text": self.review_text,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }