from pydantic import BaseModel, Field, validator, constr
from typing import Optional, List
from datetime import datetime
import re

class CategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Category name")
    description: Optional[constr] = Field(None, max_length=500, description="Category description")
    parent_id: Optional[int] = Field(None, description="Parent category ID")
    is_active: bool = Field(True, description="Whether the category is active")
    sort_order: int = Field(0, ge=0, description="Sort order for display")
    icon_url: Optional[str] = Field(None, description="Icon URL for the category")
    color_code: Optional[str] = Field('#3B82F6', description="Color code for the category")

    @validator('name')
    def validate_name(cls, v):
        if not v.strip():
            raise ValueError("Category name cannot be empty")
        if len(v) > 100:
            raise ValueError("Category name cannot exceed 100 characters")
        return v.strip()

    @validator('color_code')
    def validate_color_code(cls, v):
        if v and not re.match(r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$', v):
            raise ValueError("Invalid color code format. Use hex format like #3B82F6")
        return v

class CategoryCreate(CategoryBase):
    slug: Optional[str] = Field(None, description="URL-friendly slug. Auto-generated if not provided")

    @validator('slug')
    def validate_slug(cls, v, values):
        if v is not None:
            if not re.match(r'^[a-z0-9\-]+$', v):
                raise ValueError("Slug can only contain lowercase letters, numbers, and hyphens")
            if len(v) > 120:
                raise ValueError("Slug cannot exceed 120 characters")
        return v

class CategoryUpdate(BaseModel):
    name: Optional[constr] = Field(None, min_length=1, max_length=100, description="Category name")
    description: Optional[str] = Field(None, max_length=500, description="Category description")
    parent_id: Optional[int] = Field(None, description="Parent category ID")
    is_active: Optional[bool] = Field(None, description="Whether the category is active")
    sort_order: Optional[int] = Field(None, ge=0, description="Sort order for display")
    icon_url: Optional[str] = Field(None, description="Icon URL for the category")
    color_code: Optional[str] = Field(None, description="Color code for the category")

    @validator('name')
    def validate_name(cls, v):
        if v is not None:
            if not v.strip():
                raise ValueError("Category name cannot be empty")
            if len(v) > 100:
                raise ValueError("Category name cannot exceed 100 characters")
            return v.strip()
        return v

    @validator('color_code')
    def validate_color_code(cls, v):
        if v and not re.match(r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$', v):
            raise ValueError("Invalid color code format. Use hex format like #3B82F6")
        return v

class CategoryResponse(BaseModel):
    id: int
    name: str
    slug: str
    description: Optional[str]
    parent_id: Optional[int]
    is_active: bool
    sort_order: int
    icon_url: Optional[str]
    color_code: Optional[str]
    created_at: datetime
    updated_at: datetime
    course_count: Optional[int] = Field(None, description="Number of courses in this category")

    class Config:
        from_attributes = True

class CategoryWithChildrenResponse(CategoryResponse):
    subcategories: List['CategoryResponse'] = Field(default_factory=list)
    parent: Optional['CategoryResponse'] = None

class CategoryTreeResponse(BaseModel):
    id: int
    name: str
    slug: str
    description: Optional[str]
    is_active: bool
    sort_order: int
    icon_url: Optional[str]
    color_code: Optional[str]
    course_count: Optional[int]
    children: List['CategoryTreeResponse'] = Field(default_factory=list)

class CategoryListResponse(BaseModel):
    categories: List[CategoryResponse]
    total_count: int
    page: int
    page_size: int
    total_pages: int

# Update forward references
CategoryWithChildrenResponse.update_forward_refs()
CategoryTreeResponse.update_forward_refs()