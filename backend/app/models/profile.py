"""
User profile model for EduVerse platform
"""

from sqlalchemy import Column, String, Text, Boolean, DateTime, Integer, Float, JSON, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base
import uuid

class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.id"), unique=True)
    
    # Extended profile information
    phone_number = Column(String)
    address = Column(Text)
    city = Column(String)
    state = Column(String)
    postal_code = Column(String)
    
    # Professional information
    occupation = Column(String)
    company = Column(String)
    industry = Column(String)
    experience_level = Column(String)  # beginner, intermediate, expert
    
    # Educational background
    education_level = Column(String)
    field_of_study = Column(String)
    certifications = Column(JSON)  # List of certifications
    
    # Learning preferences
    preferred_learning_time = Column(String)  # morning, afternoon, evening
    learning_goals = Column(JSON)  # List of learning goals
    interests = Column(JSON)  # List of interests
    
    # Social features
    is_profile_public = Column(Boolean, default=False)
    allow_messages = Column(Boolean, default=True)
    show_progress = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<UserProfile(id={self.id}, user_id={self.user_id})>"