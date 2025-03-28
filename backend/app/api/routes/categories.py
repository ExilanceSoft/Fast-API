# banjos_restaurant\app\api\routes\categories.py
from fastapi import APIRouter, HTTPException
from app.schemas.categories import CategoryCreate, CategoryUpdate, CategoryResponse
from app.services.categories_service import (
    create_category,
    get_category,
    update_category,
    delete_category,
    get_all_categories,
)
from typing import List

router = APIRouter(prefix="", tags=["Categories"])

@router.post("/", response_model=CategoryResponse)
async def add_category(category: CategoryCreate):
    """Add a new category."""
    new_category = await create_category(category.dict())
    return new_category

@router.get("/", response_model=List[CategoryResponse])
async def list_categories():
    """Retrieve all categories."""
    return await get_all_categories()

@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category_by_id(category_id: str):
    """Retrieve a category by its ID."""
    category = await get_category(category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    return category

@router.put("/{category_id}", response_model=CategoryResponse)
async def update_category_by_id(category_id: str, category: CategoryUpdate):
    """Update a category by its ID."""
    updated_category = await update_category(category_id, category.dict(exclude_unset=True))
    if not updated_category:
        raise HTTPException(status_code=404, detail="Category not found")
    return updated_category

@router.delete("/{category_id}")
async def delete_category_by_id(category_id: str):
    """Delete a category by its ID."""
    if not await delete_category(category_id):
        raise HTTPException(status_code=404, detail="Category not found")
    return {"message": "Category deleted successfully"}