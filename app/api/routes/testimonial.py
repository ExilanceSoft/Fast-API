from fastapi import APIRouter, HTTPException, status, UploadFile, File, Form
from app.schemas.testimonial import TestimonialCreate, TestimonialResponse
from app.services.testimonial_service import (
    create_testimonial, 
    get_testimonial, 
    get_all_testimonials, 
    update_testimonial_status,
    delete_testimonial
)
from app.core.config import IMAGES_DIR
import os
from datetime import datetime

router = APIRouter()

@router.post("/", response_model=TestimonialResponse, status_code=status.HTTP_201_CREATED)
async def submit_testimonial(
    name: str = Form(...),
    email: str = Form(...),
    description: str = Form(...),
    rating: int = Form(...),
    image: UploadFile = File(None)
):
    testimonial_data = {
        "name": name,
        "email": email,
        "description": description,
        "rating": rating,
    }

    # Save image if provided
    if image:
        if not os.path.exists(IMAGES_DIR):
            os.makedirs(IMAGES_DIR)
        
        timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
        filename = f"{timestamp}_{image.filename}"
        image_path = os.path.join(IMAGES_DIR, filename)
        
        with open(image_path, "wb") as buffer:
            buffer.write(await image.read())
        
        testimonial_data["image"] = f"/static/images/{filename}"

    # Create testimonial
    testimonial_id = await create_testimonial(testimonial_data)
    return {**testimonial_data, "id": testimonial_id, "status": "pending", "created_at": datetime.utcnow().isoformat()}

@router.get("/{testimonial_id}", response_model=TestimonialResponse)
async def read_testimonial(testimonial_id: str):
    testimonial = await get_testimonial(testimonial_id)
    if not testimonial:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Testimonial not found")
    return testimonial

@router.get("/", response_model=list[TestimonialResponse])
async def read_all_testimonials():
    testimonials = await get_all_testimonials()
    return testimonials

@router.patch("/{testimonial_id}/status", status_code=status.HTTP_200_OK)
async def change_testimonial_status(testimonial_id: str, status: str):
    if status not in ["pending", "approved", "rejected"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid status. Must be 'pending', 'approved', or 'rejected'"
        )
    await update_testimonial_status(testimonial_id, status)
    return {"message": "Testimonial status updated successfully"}

@router.delete("/{testimonial_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_testimonial(testimonial_id: str):
    testimonial = await get_testimonial(testimonial_id)
    if not testimonial:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Testimonial not found")
    
    # Delete associated image if exists
    if testimonial.get("image"):
        image_path = os.path.join(IMAGES_DIR, testimonial["image"].split("/static/images/")[-1])
        if os.path.exists(image_path):
            os.remove(image_path)
    
    await delete_testimonial(testimonial_id)
    return None