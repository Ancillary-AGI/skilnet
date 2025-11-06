"""
Category model for EduVerse platform
"""

from sqlalchemy import Column, String, Text, Boolean, DateTime, Integer, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base
import uuid

class Category(Base):
    __tablename__ = "categories"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False, unique=True)
    slug = Column(String, unique=True, index=True)
    description = Column(Text)
    icon = Column(String)  # Icon name or emoji
    color = Column(String)  # Hex color code
    
    # Hierarchy
    parent_id = Column(String)
    sort_order = Column(Integer, default=0)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Statistics
    course_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Relationships
    courses = relationship("Course", back_populates="category")

    def __repr__(self):
        return f"<Category(id={self.id}, name={self.name})>"
