from typing import List, Optional
from fastapi import HTTPException, UploadFile
from app.core.database import dynamodb
from app.schemas.image import ImageResponse
from datetime import datetime
import os
import uuid

async def create_image(image_data: dict, file: UploadFile) -> ImageResponse:
    """Create a new image."""
    try:
        # Save the file to the static/images directory
        file_path = f"static/images/{file.filename}"
        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())

        # Generate a unique ID for the image
        image_id = str(uuid.uuid4())
        image_data["id"] = image_id
        image_data["file_path"] = file_path
        image_data["created_at"] = datetime.utcnow().isoformat()

        # Ensure description is not None
        if image_data.get("description") is None:
            image_data["description"] = ""

        # Insert into DynamoDB
        item = {
            "Home": {"S": "Images"},  # Partition key
            "1": {"S": image_id},     # Sort key
            "name": {"S": image_data["name"]},
            "description": {"S": image_data["description"]},  # Ensure this is a string
            "category_id": {"S": image_data["category_id"]},
            "file_path": {"S": image_data["file_path"]},
            "created_at": {"S": image_data["created_at"]}
        }

        await dynamodb.put_item(item)
        return ImageResponse(**image_data)
    except Exception as e:
        print(f"Error creating image: {e}")
        raise HTTPException(status_code=500, detail="Failed to create image")

async def get_image(image_id: str) -> Optional[ImageResponse]:
    """Retrieve an image by ID."""
    try:
        key = {
            "Home": {"S": "Images"},  # Partition key
            "1": {"S": image_id}      # Sort key
        }
        item = await dynamodb.get_item(key)
        if item:
            image_data = {
                "id": item.get("1", {}).get("S", ""),
                "name": item.get("name", {}).get("S", ""),
                "description": item.get("description", {}).get("S", ""),
                "category_id": item.get("category_id", {}).get("S", ""),
                "file_path": item.get("file_path", {}).get("S", ""),
                "created_at": item.get("created_at", {}).get("S", "")
            }
            return ImageResponse(**image_data)
        return None
    except Exception as e:
        print(f"Error retrieving image: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve image")

async def get_all_images() -> List[ImageResponse]:
    """Retrieve all images."""
    try:
        items = await dynamodb.scan()
        images = []
        for item in items:
            if item.get("Home", {}).get("S") == "Images":  # Filter by partition key
                image_data = {
                    "id": item.get("1", {}).get("S", ""),
                    "name": item.get("name", {}).get("S", ""),
                    "description": item.get("description", {}).get("S", ""),
                    "category_id": item.get("category_id", {}).get("S", ""),
                    "file_path": item.get("file_path", {}).get("S", ""),
                    "created_at": item.get("created_at", {}).get("S", "")
                }
                images.append(ImageResponse(**image_data))
        return images
    except Exception as e:
        print(f"Error retrieving images: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve images")

async def update_image(image_id: str, image_data: dict, file: Optional[UploadFile] = None) -> Optional[ImageResponse]:
    """Update an image by ID."""
    try:
        if file:
            # Save the new file to the static/images directory
            file_path = f"static/images/{file.filename}"
            with open(file_path, "wb") as buffer:
                buffer.write(await file.read())
            image_data["file_path"] = file_path

        # Ensure description is not None
        if image_data.get("description") is None:
            image_data["description"] = ""

        key = {
            "Home": {"S": "Images"},  # Partition key
            "1": {"S": image_id}      # Sort key
        }

        update_expression = "SET "
        expression_attribute_names = {}
        expression_attribute_values = {}

        for field, value in image_data.items():
            if value is not None:  # Only update fields that are provided
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
        return await get_image(image_id)
    except Exception as e:
        print(f"Error updating image: {e}")
        raise HTTPException(status_code=500, detail="Failed to update image")

async def delete_image(image_id: str) -> bool:
    """Delete an image by ID."""
    try:
        key = {
            "Home": {"S": "Images"},  # Partition key
            "1": {"S": image_id}      # Sort key
        }
        await dynamodb.delete_item(key)
        return True
    except Exception as e:
        print(f"Error deleting image: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete image")