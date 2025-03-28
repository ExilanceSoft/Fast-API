from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from typing import List, Optional
from app.schemas.gallery_cat import GalleryCreate, GalleryCategoryUpdate, GalleryCategoryResponse
from app.services.gallery_cat_service import (
    create_gallery_category,
    get_gallery_category,
    get_all_gallery_categories,
    update_gallery_category,
    delete_gallery_category,
)

router = APIRouter(prefix="", tags=["Gallery"])

@router.post("/categories/add", response_model=GalleryCategoryResponse)
async def add_gallery_category(
    name: str = Form(...),
    image: Optional[UploadFile] = File(None)
):
    """Add a new gallery category with optional image."""
    category_data = {"name": name}
    new_category = await create_gallery_category(category_data, image)
    return new_category

@router.get("/categories", response_model=List[GalleryCategoryResponse])
async def list_gallery_categories():
    """Retrieve all gallery categories."""
    return await get_all_gallery_categories()

@router.get("/categories/{category_id}", response_model=GalleryCategoryResponse)
async def get_gallery_category_by_id(category_id: str):
    """Retrieve a gallery category by its ID."""
    category = await get_gallery_category(category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Gallery category not found")
    return category

@router.put("/categories/{category_id}", response_model=GalleryCategoryResponse)
async def update_gallery_category_by_id(
    category_id: str,
    name: Optional[str] = Form(None),
    image: Optional[UploadFile] = File(None)
):
    """Update a gallery category by its ID."""
    category_data = {}
    if name is not None:
        category_data["name"] = name
    
    updated_category = await update_gallery_category(category_id, category_data, image)
    if not updated_category:
        raise HTTPException(status_code=404, detail="Gallery category not found")
    return updated_category

@router.delete("/categories/{category_id}")
async def delete_gallery_category_by_id(category_id: str):
    """Delete a gallery category by its ID."""
    if not await delete_gallery_category(category_id):
        raise HTTPException(status_code=404, detail="Gallery category not found")
    return {"message": "Gallery category deleted successfully"}