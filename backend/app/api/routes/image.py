from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import List, Optional
from app.schemas.image import ImageCreate, ImageUpdate, ImageResponse
from app.services.image_service import (
    create_image,
    get_image,
    get_all_images,
    update_image,
    delete_image,
)

router = APIRouter(prefix="/images", tags=["Images"])

@router.post("/add", response_model=ImageResponse)
async def add_image(
    name: str,
    category_id: str,
    file: UploadFile = File(...),
    description: Optional[str] = None
):
    """Add a new image."""
    image_data = {
        "name": name,
        "description": description,
        "category_id": category_id
    }
    new_image = await create_image(image_data, file)
    return new_image

@router.get("/", response_model=List[ImageResponse])
async def list_images():
    """Retrieve all images."""
    return await get_all_images()

@router.get("/{image_id}", response_model=ImageResponse)
async def get_image_by_id(image_id: str):
    """Retrieve an image by its ID."""
    image = await get_image(image_id)
    if not image:
        raise HTTPException(status_code=404, detail="Image not found")
    return image

@router.put("/{image_id}", response_model=ImageResponse)
async def update_image_by_id(
    image_id: str,
    name: str,
    category_id: str,
    description: Optional[str] = None,
    file: Optional[UploadFile] = File(None)
):
    """Update an image by its ID."""
    image_data = {
        "name": name,
        "category_id": category_id,
        "description": description,
    }
    updated_image = await update_image(image_id, image_data, file)
    if not updated_image:
        raise HTTPException(status_code=404, detail="Image not found")
    return updated_image

@router.delete("/{image_id}")
async def delete_image_by_id(image_id: str):
    """Delete an image by its ID."""
    if not await delete_image(image_id):
        raise HTTPException(status_code=404, detail="Image not found")
    return {"message": "Image deleted successfully"}