"""
User model with comprehensive authentication and profile features
"""

from sqlalchemy import Column, String, Boolean, DateTime, Text, JSON, Integer, Float
from sqlalchemy.dialects.postgresql import UUID, ARRAY
from sqlalchemy.sql import func
import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any

from app.core.database import Base


class User(Base):
    """User model with advanced features"""
    __tablename__ = "users"
    
    # Primary identification
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, index=True, nullable=False)
    username = Column(String(50), unique=True, index=True, nullable=False)
    
    # Authentication
    hashed_password = Column(String(255), nullable=True)  # Optional for OAuth users
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    is_superuser = Column(Boolean, default=False)
    
    # Profile information
    first_name = Column(String(100))
    last_name = Column(String(100))
    display_name = Column(String(150))
    bio = Column(Text)
    avatar_url = Column(String(500))
    
    # Learning preferences
    learning_style = Column(String(50))  # visual, auditory, kinesthetic, reading
    preferred_language = Column(String(10), default="en")
    timezone = Column(String(50), default="UTC")
    
    # Gamification
    experience_points = Column(Integer, default=0)
    level = Column(Integer, default=1)
    badges = Column(ARRAY(String), default=list)
    streak_days = Column(Integer, default=0)
    
    # VR/AR Preferences
    vr_comfort_level = Column(String(20), default="comfortable")  # comfortable, sensitive, expert
    preferred_vr_environment = Column(String(50), default="classroom")
    motion_sickness_settings = Column(JSON, default=dict)
    
    # AI Interaction Preferences
    ai_interaction_style = Column(String(30), default="friendly")  # formal, friendly, casual
    preferred_ai_voice = Column(String(50), default="neutral")
    ai_difficulty_adaptation = Column(Boolean, default=True)
    
    # Security & Authentication
    two_factor_enabled = Column(Boolean, default=False)
    two_factor_secret = Column(String(32))
    webauthn_credentials = Column(JSON, default=list)  # Store passkey credentials
    oauth_providers = Column(ARRAY(String), default=list)
    
    # Activity tracking
    last_login = Column(DateTime(timezone=True))
    last_activity = Column(DateTime(timezone=True))
    login_count = Column(Integer, default=0)
    
    # Subscription & Billing
    subscription_tier = Column(String(20), default="free")  # free, premium, enterprise
    subscription_expires = Column(DateTime(timezone=True))
    
    # Privacy settings
    profile_visibility = Column(String(20), default="public")  # public, friends, private
    data_sharing_consent = Column(Boolean, default=False)
    marketing_consent = Column(Boolean, default=False)
    
    # Accessibility
    accessibility_settings = Column(JSON, default=dict)
    screen_reader_enabled = Column(Boolean, default=False)
    high_contrast_mode = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, username={self.username})>"
    
    @property
    def full_name(self) -> str:
        """Get user's full name"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.display_name or self.username
    
    @property
    def is_premium(self) -> bool:
        """Check if user has premium subscription"""
        if self.subscription_tier in ["premium", "enterprise"]:
            if self.subscription_expires and self.subscription_expires > datetime.utcnow():
                return True
        return False
    
    def add_experience_points(self, points: int) -> None:
        """Add experience points and update level"""
        self.experience_points += points
        # Simple leveling system: level = sqrt(xp / 100)
        new_level = int((self.experience_points / 100) ** 0.5) + 1
        if new_level > self.level:
            self.level = new_level
    
    def add_badge(self, badge_name: str) -> None:
        """Add a badge to user's collection"""
        if self.badges is None:
            self.badges = []
        if badge_name not in self.badges:
            self.badges.append(badge_name)
    
    def update_streak(self, active_today: bool) -> None:
        """Update learning streak"""
        if active_today:
            self.streak_days += 1
        else:
            self.streak_days = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert user to dictionary for API responses"""
        return {
            "id": str(self.id),
            "email": self.email,
            "username": self.username,
            "full_name": self.full_name,
            "avatar_url": self.avatar_url,
            "bio": self.bio,
            "level": self.level,
            "experience_points": self.experience_points,
            "badges": self.badges or [],
            "streak_days": self.streak_days,
            "subscription_tier": self.subscription_tier,
            "is_premium": self.is_premium,
            "learning_style": self.learning_style,
            "preferred_language": self.preferred_language,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }