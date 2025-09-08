from fastapi import APIRouter, Depends, HTTPException, status, Query
from typing import List, Optional
from pydantic import BaseModel

from models.category import Category
from schemas.category import (
    CategoryCreate, 
    CategoryUpdate, 
    CategoryResponse, 
    CategoryWithChildrenResponse,
    CategoryTreeResponse,
    CategoryListResponse
)
from services.category_service import CategoryService
from api.dependencies import get_current_user

router = APIRouter(prefix="/categories", tags=["categories"])

class BulkSortRequest(BaseModel):
    categories: List[dict]

@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    category_data: CategoryCreate,
    current_user = Depends(get_current_user)
):
    """Create a new category"""
    if current_user.role not in ['admin', 'instructor']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins and instructors can create categories"
        )
    
    try:
        category = await CategoryService.create_category(category_data)
        return category.to_dict()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/", response_model=CategoryListResponse)
async def get_categories(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    parent_id: Optional[int] = Query(None),
    is_active: Optional[bool] = Query(None),
    search: Optional[str] = Query(None)
):
    """Get paginated list of categories"""
    result = await CategoryService.get_categories(
        page=page,
        page_size=page_size,
        parent_id=parent_id,
        is_active=is_active,
        search=search
    )
    
    return CategoryListResponse(
        categories=result['categories'],
        total_count=result['total'],
        page=result['page'],
        page_size=result['page_size'],
        total_pages=result['total_pages']
    )

@router.get("/tree", response_model=List[CategoryTreeResponse])
async def get_category_tree():
    """Get the complete category hierarchy as a tree"""
    return await CategoryService.get_category_tree()

@router.get("/{category_id}", response_model=CategoryWithChildrenResponse)
async def get_category(category_id: int):
    """Get a specific category with its subcategories"""
    category = await CategoryService.get_category(category_id, include_relations=True)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    category_dict = category.to_dict()
    category_dict['course_count'] = await category.get_course_count()
    
    # Get subcategories
    subcategories = await category.get_subcategories()
    category_dict['subcategories'] = [subcat.to_dict() for subcat in subcategories]
    
    # Get parent if exists
    if category.parent_id:
        parent = await Category.get(category.parent_id)
        category_dict['parent'] = parent.to_dict() if parent else None
    
    return category_dict

@router.get("/slug/{slug}", response_model=CategoryWithChildrenResponse)
async def get_category_by_slug(slug: str):
    """Get a category by its slug"""
    category = await CategoryService.get_category_by_slug(slug)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    category_dict = category.to_dict()
    category_dict['course_count'] = await category.get_course_count()
    
    # Get subcategories
    subcategories = await category.get_subcategories()
    category_dict['subcategories'] = [subcat.to_dict() for subcat in subcategories]
    
    return category_dict

@router.put("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: int,
    category_data: CategoryUpdate,
    current_user = Depends(get_current_user)
):
    """Update a category"""
    if current_user.role not in ['admin', 'instructor']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins and instructors can update categories"
        )
    
    category = await CategoryService.update_category(category_id, category_data)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    return category.to_dict()

@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: int,
    current_user = Depends(get_current_user)
):
    """Delete a category"""
    if current_user.role != 'admin':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can delete categories"
        )
    
    try:
        success = await CategoryService.delete_category(category_id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.patch("/{category_id}/move", response_model=CategoryResponse)
async def move_category(
    category_id: int,
    new_parent_id: Optional[int] = Query(None),
    current_user = Depends(get_current_user)
):
    """Move category to a new parent"""
    if current_user.role not in ['admin', 'instructor']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins and instructors can move categories"
        )
    
    try:
        category = await CategoryService.move_category(category_id, new_parent_id)
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Category not found"
            )
        return category.to_dict()
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.patch("/bulk-sort", status_code=status.HTTP_200_OK)
async def bulk_update_sort_order(
    sort_data: BulkSortRequest,
    current_user = Depends(get_current_user)
):
    """Update sort order for multiple categories"""
    if current_user.role not in ['admin', 'instructor']:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins and instructors can update sort order"
        )
    
    success = await CategoryService.bulk_update_sort_order(sort_data.categories)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to update sort order"
        )
    
    return {"message": "Sort order updated successfully"}