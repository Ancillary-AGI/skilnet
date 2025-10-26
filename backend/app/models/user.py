"""
User model for EduVerse platform
"""

from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, JSON, Float
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base
from datetime import datetime
from typing import Optional, Dict, Any
import uuid

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=True)
    full_name = Column(String, nullable=True)
    hashed_password = Column(String, nullable=True)
    
    # Profile information
    avatar_url = Column(String, nullable=True)
    bio = Column(Text, nullable=True)
    date_of_birth = Column(DateTime, nullable=True)
    country_code = Column(String(2), nullable=True)
    timezone = Column(String, nullable=True)
    language_preference = Column(String, default="en")
    
    # Account status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    is_premium = Column(Boolean, default=False)
    is_instructor = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)
    
    # Social login
    google_id = Column(String, nullable=True)
    apple_id = Column(String, nullable=True)
    facebook_id = Column(String, nullable=True)
    
    # Learning preferences
    learning_style = Column(String, nullable=True)  # visual, auditory, kinesthetic
    difficulty_preference = Column(String, default="intermediate")
    daily_goal_minutes = Column(Integer, default=30)
    
    # Gamification
    total_xp = Column(Integer, default=0)
    current_level = Column(Integer, default=1)
    current_streak = Column(Integer, default=0)
    longest_streak = Column(Integer, default=0)
    
    # Accessibility
    accessibility_settings = Column(JSON, nullable=True)
    
    # External IDs for payment processing
    stripe_customer_id = Column(String, nullable=True)
    paypal_customer_id = Column(String, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    last_login_at = Column(DateTime, nullable=True)
    email_verified_at = Column(DateTime, nullable=True)
    
    # Relationships
    # courses = relationship("Course", back_populates="instructor")
    # enrollments = relationship("Enrollment", back_populates="user")
    # subscriptions = relationship("Subscription", back_populates="user")
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, full_name={self.full_name})>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert user to dictionary"""
        return {
            "id": self.id,
            "email": self.email,
            "username": self.username,
            "full_name": self.full_name,
            "avatar_url": self.avatar_url,
            "bio": self.bio,
            "country_code": self.country_code,
            "language_preference": self.language_preference,
            "is_active": self.is_active,
            "is_verified": self.is_verified,
            "is_premium": self.is_premium,
            "is_instructor": self.is_instructor,
            "total_xp": self.total_xp,
            "current_level": self.current_level,
            "current_streak": self.current_streak,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "last_login_at": self.last_login_at.isoformat() if self.last_login_at else None,
        }
    
    @property
    def display_name(self) -> str:
        """Get display name for user"""
        return self.full_name or self.username or self.email.split("@")[0]
    
    @property
    def is_social_user(self) -> bool:
        """Check if user registered via social login"""
        return bool(self.google_id or self.apple_id or self.facebook_id)
    
    def calculate_level(self) -> int:
        """Calculate user level based on XP"""
        if self.total_xp < 100:
            return 1
        return min(int(self.total_xp / 100) + 1, 100)
    
    def xp_to_next_level(self) -> int:
        """Calculate XP needed for next level"""
        current_level_xp = (self.current_level - 1) * 100
        next_level_xp = self.current_level * 100
        return next_level_xp - self.total_xp
    
    def add_xp(self, amount: int) -> bool:
        """Add XP and check for level up"""
        old_level = self.current_level
        self.total_xp += amount
        self.current_level = self.calculate_level()
        return self.current_level > old_level
    
    def update_streak(self, completed_today: bool = True) -> None:
        """Update learning streak"""
        if completed_today:
            self.current_streak += 1
            if self.current_streak > self.longest_streak:
                self.longest_streak = self.current_streak
        else:
            self.current_streak = 0