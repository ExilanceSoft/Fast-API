from typing import List, Optional
from fastapi import HTTPException, UploadFile
from app.core.database import dynamodb
from app.schemas.gallery_cat import GalleryCategoryResponse
from datetime import datetime
import uuid
import os
from pathlib import Path

# Ensure static/images directory exists
os.makedirs("static/images/gallery", exist_ok=True)

async def save_image(file: UploadFile) -> str:
    """Save an uploaded image and return the file path."""
    # Generate unique filename to prevent collisions
    file_ext = os.path.splitext(file.filename)[1]
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    file_path = f"static/images/gallery/{unique_filename}"
    
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())
    
    return f"/{file_path}"

async def create_gallery_category(category_data: dict, image: Optional[UploadFile] = None) -> GalleryCategoryResponse:
    """Create a new gallery category with optional image."""
    try:
        # Save image if provided
        if image:
            category_data["image_url"] = await save_image(image)
        else:
            category_data["image_url"] = ""

        # Generate a unique ID for the category
        category_id = str(uuid.uuid4())
        category_data["id"] = category_id
        category_data["created_at"] = datetime.utcnow().isoformat()

        # Insert into DynamoDB
        item = {
            "Home": {"S": "GalleryCategories"},
            "1": {"S": category_id},
            "name": {"S": category_data["name"]},
            "image_url": {"S": category_data["image_url"]},
            "created_at": {"S": category_data["created_at"]}
        }

        await dynamodb.put_item(item)
        return GalleryCategoryResponse(**category_data)
    except Exception as e:
        print(f"Error creating gallery category: {e}")
        raise HTTPException(status_code=500, detail="Failed to create gallery category")

async def get_gallery_category(category_id: str) -> Optional[GalleryCategoryResponse]:
    """Retrieve a gallery category by ID."""
    try:
        key = {
            "Home": {"S": "GalleryCategories"},
            "1": {"S": category_id}
        }
        item = await dynamodb.get_item(key)
        if item:
            category_data = {
                "id": item.get("1", {}).get("S", ""),
                "name": item.get("name", {}).get("S", ""),
                "image_url": item.get("image_url", {}).get("S", ""),
                "created_at": item.get("created_at", {}).get("S", "")
            }
            return GalleryCategoryResponse(**category_data)
        return None
    except Exception as e:
        print(f"Error retrieving gallery category: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve gallery category")

async def get_all_gallery_categories() -> List[GalleryCategoryResponse]:
    """Retrieve all gallery categories."""
    try:
        items = await dynamodb.scan()
        categories = []
        for item in items:
            if item.get("Home", {}).get("S") == "GalleryCategories":
                category_data = {
                    "id": item.get("1", {}).get("S", ""),
                    "name": item.get("name", {}).get("S", ""),
                    "image_url": item.get("image_url", {}).get("S", ""),
                    "created_at": item.get("created_at", {}).get("S", "")
                }
                categories.append(GalleryCategoryResponse(**category_data))
        return categories
    except Exception as e:
        print(f"Error retrieving gallery categories: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve gallery categories")

async def update_gallery_category(category_id: str, category_data: dict, image: Optional[UploadFile] = None) -> Optional[GalleryCategoryResponse]:
    """Update a gallery category by ID."""
    try:
        # Save new image if provided
        if image:
            category_data["image_url"] = await save_image(image)

        key = {
            "Home": {"S": "GalleryCategories"},
            "1": {"S": category_id}
        }

        update_expression = "SET "
        expression_attribute_names = {}
        expression_attribute_values = {}

        for field, value in category_data.items():
            if value is not None:
                expression_attribute_names[f"#{field}"] = field
                update_expression += f"#{field} = :{field}, "
                expression_attribute_values[f":{field}"] = {"S": str(value)}

        update_expression = update_expression.rstrip(", ")

        await dynamodb.update_item(
            key=key,
            update_expression=update_expression,
            expression_attribute_names=expression_attribute_names,
            expression_attribute_values=expression_attribute_values
        )
        return await get_gallery_category(category_id)
    except Exception as e:
        print(f"Error updating gallery category: {e}")
        raise HTTPException(status_code=500, detail="Failed to update gallery category")

async def delete_gallery_category(category_id: str) -> bool:
    """Delete a gallery category by ID."""
    try:
        key = {
            "Home": {"S": "GalleryCategories"},
            "1": {"S": category_id}
        }
        await dynamodb.delete_item(key)
        return True
    except Exception as e:
        print(f"Error deleting gallery category: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete gallery category")