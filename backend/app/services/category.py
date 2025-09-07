# services/category_service.py
from typing import List, Optional, Dict, Any
from models.category import Category
from schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse, CategoryTreeResponse

class CategoryService:
    
    @staticmethod
    async def create_category(category_data: CategoryCreate) -> Category:
        """Create a new category"""
        data = category_data.dict(exclude_unset=True)
        return await Category.create(**data)
    
    @staticmethod
    async def get_category(category_id: int, include_relations: bool = False) -> Optional[Category]:
        """Get a category by ID"""
        category = await Category.get(category_id)
        if category and include_relations:
            await category.prefetch_relations('parent', 'courses')
        return category
    
    @staticmethod
    async def update_category(category_id: int, update_data: CategoryUpdate) -> Optional[Category]:
        """Update a category"""
        category = await Category.get(category_id)
        if not category:
            return None
        
        update_dict = update_data.dict(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(category, field, value)
        
        await category.save()
        return category
    
    @staticmethod
    async def delete_category(category_id: int) -> bool:
        """Delete a category"""
        category = await Category.get(category_id)
        if not category:
            return False
        
        # Check if category has courses
        course_count = await category.get_course_count()
        if course_count > 0:
            raise ValueError("Cannot delete category with associated courses")
        
        # Check if category has subcategories
        subcategories = await category.get_subcategories()
        if subcategories:
            raise ValueError("Cannot delete category with subcategories. Move or delete subcategories first.")
        
        await category.delete()
        return True
    
    @staticmethod
    async def get_categories(
        page: int = 1,
        page_size: int = 20,
        parent_id: Optional[int] = None,
        is_active: Optional[bool] = None,
        search: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get paginated list of categories"""
        query = Category.query()
        
        if parent_id is not None:
            query = query.filter(parent_id=parent_id)
        else:
            query = query.filter(parent_id__is_null=True)  # Only root categories
        
        if is_active is not None:
            query = query.filter(is_active=is_active)
        
        if search:
            query = query.filter(name__ilike=f"%{search}%")
        
        query = query.order_by('sort_order', 'name')
        
        result = await query.paginate(page, page_size)
        
        # Add course counts to each category
        categories_with_counts = []
        for category in result.items:
            category_dict = category.to_dict()
            category_dict['course_count'] = await category.get_course_count()
            categories_with_counts.append(category_dict)
        
        return {
            'categories': categories_with_counts,
            'total': result.total,
            'page': result.page,
            'page_size': result.page_size,
            'total_pages': result.total_pages
        }
    
    @staticmethod
    async def get_category_tree() -> List[CategoryTreeResponse]:
        """Get the complete category hierarchy as a tree"""
        root_categories = await Category.query().filter(parent_id__is_null=True, is_active=True).order_by('sort_order', 'name').execute()
        
        tree = []
        for category in root_categories:
            tree.append(await CategoryService._build_category_tree(category))
        
        return tree
    
    @staticmethod
    async def _build_category_tree(category: Category) -> CategoryTreeResponse:
        """Recursively build category tree"""
        subcategories = await category.get_subcategories()
        course_count = await category.get_course_count()
        
        children = []
        for subcategory in subcategories:
            children.append(await CategoryService._build_category_tree(subcategory))
        
        return CategoryTreeResponse(
            id=category.id,
            name=category.name,
            slug=category.slug,
            description=category.description,
            is_active=category.is_active,
            sort_order=category.sort_order,
            icon_url=category.icon_url,
            color_code=category.color_code,
            course_count=course_count,
            children=children
        )
    
    @staticmethod
    async def get_category_by_slug(slug: str) -> Optional[Category]:
        """Get category by slug"""
        categories = await Category.query().filter(slug=slug).execute()
        return categories[0] if categories else None
    
    @staticmethod
    async def move_category(category_id: int, new_parent_id: Optional[int]) -> Optional[Category]:
        """Move category to a new parent"""
        category = await Category.get(category_id)
        if not category:
            return None
        
        # Check for circular reference
        if new_parent_id:
            if category_id == new_parent_id:
                raise ValueError("Category cannot be its own parent")
            
            # Check if new parent is a descendant of this category
            new_parent = await Category.get(new_parent_id)
            if new_parent:
                parent_chain = await new_parent.get_parent_chain()
                if any(cat.id == category_id for cat in parent_chain):
                    raise ValueError("Cannot create circular category hierarchy")
        
        category.parent_id = new_parent_id
        await category.save()
        return category
    
    @staticmethod
    async def bulk_update_sort_order(sort_data: List[Dict[str, Any]]) -> bool:
        """Update sort order for multiple categories"""
        updates = []
        for item in sort_data:
            if 'id' in item and 'sort_order' in item:
                updates.append((item['id'], item['sort_order']))
        
        if not updates:
            return False
        
        # Update each category
        for category_id, sort_order in updates:
            category = await Category.get(category_id)
            if category:
                category.sort_order = sort_order
                await category.save()
        
        return True