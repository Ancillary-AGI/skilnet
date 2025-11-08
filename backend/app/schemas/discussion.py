"""
Pydantic schemas for discussion forums
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

class DiscussionPostCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    content: str = Field(..., min_length=1)
    course_id: Optional[str] = None
    post_type: Optional[str] = "discussion"

class DiscussionPostUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    content: Optional[str] = Field(None, min_length=1)

class DiscussionPostResponse(BaseModel):
    id: str
    title: str
    content: str
    author: str
    author_avatar: Optional[str]
    timestamp: datetime
    likes: int
    replies_count: int
    post_type: str

class DiscussionReplyCreate(BaseModel):
    content: str = Field(..., min_length=1)

class DiscussionReplyResponse(BaseModel):
    id: str
    content: str
    author: str
    author_avatar: Optional[str]
    timestamp: datetime
