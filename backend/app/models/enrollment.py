"""
Enrollment model for EduVerse platform
"""

from sqlalchemy import Column, String, Integer, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime
from typing import Dict, Any
import uuid

class Enrollment(Base):
    __tablename__ = "enrollments"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), nullable=False, index=True)
    course_id = Column(String, ForeignKey("courses.id"), nullable=False, index=True)

    # Progress tracking
    progress_percentage = Column(Float, default=0.0)  # 0-100
    is_completed = Column(Boolean, default=False)
    completed_at = Column(DateTime)

    # Learning analytics
    time_spent_minutes = Column(Integer, default=0)
    last_accessed_at = Column(DateTime)
    lessons_completed = Column(Integer, default=0)
    total_lessons = Column(Integer, default=0)

    # Assessment scores
    quiz_score = Column(Float, nullable=True)  # Average quiz score
    final_score = Column(Float, nullable=True)  # Final assessment score

    # Engagement metrics
    login_count = Column(Integer, default=0)
    discussion_posts = Column(Integer, default=0)
    peer_interactions = Column(Integer, default=0)

    # Certificate
    certificate_issued = Column(Boolean, default=False)
    certificate_url = Column(String, nullable=True)

    # Status
    is_active = Column(Boolean, default=True)  # Can be deactivated by admin

    # Timestamps
    enrolled_at = Column(DateTime, server_default=func.now())
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="enrollments")
    course = relationship("Course", back_populates="enrollments")

    def __repr__(self):
        return f"<Enrollment(user_id={self.user_id}, course_id={self.course_id}, progress={self.progress_percentage}%)>"

    def to_dict(self) -> Dict[str, Any]:
        """Convert enrollment to dictionary"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "course_id": self.course_id,
            "progress_percentage": self.progress_percentage,
            "is_completed": self.is_completed,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "time_spent_minutes": self.time_spent_minutes,
            "last_accessed_at": self.last_accessed_at.isoformat() if self.last_accessed_at else None,
            "lessons_completed": self.lessons_completed,
            "total_lessons": self.total_lessons,
            "quiz_score": self.quiz_score,
            "final_score": self.final_score,
            "certificate_issued": self.certificate_issued,
            "certificate_url": self.certificate_url,
            "enrolled_at": self.enrolled_at.isoformat() if self.enrolled_at else None,
        }

    @property
    def completion_rate(self) -> float:
        """Calculate completion rate based on lessons"""
        if self.total_lessons == 0:
            return 0.0
        return (self.lessons_completed / self.total_lessons) * 100

    @property
    def days_enrolled(self) -> int:
        """Calculate days since enrollment"""
        if not self.enrolled_at:
            return 0
        return (datetime.utcnow() - self.enrolled_at).days

    @property
    def is_overdue(self) -> bool:
        """Check if enrollment is overdue (no activity for 30+ days)"""
        if not self.last_accessed_at:
            return self.days_enrolled > 30
        return (datetime.utcnow() - self.last_accessed_at).days > 30

    def update_progress(self, new_progress: float, lesson_completed: bool = False) -> None:
        """Update enrollment progress"""
        self.progress_percentage = min(100.0, max(0.0, new_progress))
        self.last_accessed_at = datetime.utcnow()

        if lesson_completed:
            self.lessons_completed += 1

        # Auto-complete if progress reaches 100%
        if self.progress_percentage >= 100.0 and not self.is_completed:
            self.is_completed = True
            self.completed_at = datetime.utcnow()

    def add_time_spent(self, minutes: int) -> None:
        """Add time spent on course"""
        self.time_spent_minutes += minutes
        self.last_accessed_at = datetime.utcnow()
        self.login_count += 1

    def update_scores(self, quiz_score: float = None, final_score: float = None) -> None:
        """Update assessment scores"""
        if quiz_score is not None:
            self.quiz_score = quiz_score
        if final_score is not None:
            self.final_score = final_score
            # Auto-complete if final score is provided
            if not self.is_completed:
                self.is_completed = True
                self.completed_at = datetime.utcnow()

    def issue_certificate(self, certificate_url: str) -> None:
        """Issue completion certificate"""
        self.certificate_issued = True
        self.certificate_url = certificate_url
        self.is_completed = True
        if not self.completed_at:
            self.completed_at = datetime.utcnow()

    @property
    def grade(self) -> str:
        """Calculate letter grade based on final score"""
        if self.final_score is None:
            return "N/A"

        if self.final_score >= 90:
            return "A"
        elif self.final_score >= 80:
            return "B"
        elif self.final_score >= 70:
            return "C"
        elif self.final_score >= 60:
            return "D"
        else:
            return "F"

    @property
    def status(self) -> str:
        """Get enrollment status"""
        if not self.is_active:
            return "inactive"
        elif self.is_completed:
            return "completed"
        elif self.progress_percentage > 0:
            return "in_progress"
        else:
            return "enrolled"
