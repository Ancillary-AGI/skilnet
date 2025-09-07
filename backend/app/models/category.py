# models/category.py
from .base_model import BaseModel, Relationship, RelationshipType
from ..core.database import Field
from datetime import datetime
from typing import List
import re

class Category(BaseModel):
    _table_name = "categories"
    _migration_version = 1
    
    _columns = {
        'id': Field('INTEGER', primary_key=True, autoincrement=True),
        'name': Field('TEXT', unique=True, nullable=False, index=True),
        'slug': Field('TEXT', unique=True, nullable=False, index=True),
        'description': Field('TEXT'),
        'parent_id': Field('INTEGER'),  # For hierarchical categories
        'is_active': Field('BOOLEAN', default=True),
        'sort_order': Field('INTEGER', default=0),
        'icon_url': Field('TEXT'),
        'color_code': Field('TEXT', default='#3B82F6'),  # Default blue color
        'created_at': Field('TIMESTAMP', default=datetime.now),
        'updated_at': Field('TIMESTAMP', default=datetime.now)
    }
    
    # Relationships
    _relationships = {
        'parent': Relationship(
            model_class='Category',
            relationship_type=RelationshipType.MANY_TO_ONE,
            foreign_key='parent_id',
            local_key='id',
            backref='subcategories'
        ),
        'courses': Relationship(
            model_class='Course',
            relationship_type=RelationshipType.ONE_TO_MANY,
            foreign_key='category_id',
            local_key='id',
            backref='category'
        )
    }
    
    @classmethod
    async def create(cls, **kwargs) -> 'Category':
        """Create category with automatic slug generation"""
        if 'name' in kwargs and 'slug' not in kwargs:
            kwargs['slug'] = cls.generate_slug(kwargs['name'])
        return await super().create(**kwargs)
    
    @staticmethod
    def generate_slug(name: str) -> str:
        """Generate URL-friendly slug from category name"""
        # Convert to lowercase
        slug = name.lower()
        # Replace spaces with hyphens
        slug = re.sub(r'\s+', '-', slug)
        # Remove special characters
        slug = re.sub(r'[^a-z0-9\-]', '', slug)
        # Remove consecutive hyphens
        slug = re.sub(r'\-+', '-', slug)
        # Remove leading/trailing hyphens
        slug = slug.strip('-')
        return slug
    
    async def get_subcategories(self) -> List['Category']:
        """Get all direct subcategories of this category"""
        return await Category.query().filter(parent_id=self.id).order_by('sort_order', 'name').execute()
    
    async def get_all_subcategories(self) -> List['Category']:
        """Get all subcategories recursively"""
        subcategories = await self.get_subcategories()
        all_subcategories = list(subcategories)
        
        for subcategory in subcategories:
            all_subcategories.extend(await subcategory.get_all_subcategories())
        
        return all_subcategories
    
    async def get_parent_chain(self) -> List['Category']:
        """Get the parent chain up to the root category"""
        chain = []
        current = self
        
        while current and current.parent_id:
            parent = await Category.get(current.parent_id)
            if parent:
                chain.insert(0, parent)
                current = parent
            else:
                break
        
        return chain
    
    async def get_course_count(self) -> int:
        """Get the number of courses in this category"""
        from .course import Course
        return await Course.query().filter(category_id=self.id, is_published=True).count()
    
    async def get_total_course_count(self) -> int:
        """Get total course count including subcategories"""
        from .course import Course
        
        # Get all category IDs including subcategories
        category_ids = [self.id]
        subcategories = await self.get_all_subcategories()
        category_ids.extend([cat.id for cat in subcategories])
        
        return await Course.query().filter(category_id__in=category_ids, is_published=True).count()