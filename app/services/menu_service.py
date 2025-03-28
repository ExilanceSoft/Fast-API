# banjos_restaurant\app\services\menu_service.py
import os
import uuid
from typing import Optional, List
from fastapi import UploadFile, HTTPException
from app.core.database import dynamodb
from app.models.menu import MenuModel
from datetime import datetime

# Ensure the static/images directory exists
os.makedirs("static/images", exist_ok=True)

async def save_image(file: UploadFile) -> str:
    """Save an uploaded image to the static/images folder and return the file path."""
    file_path = f"static/images/{file.filename}"
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())
    return f"/static/images/{file.filename}"

async def create_menu_item(menu_data: dict, image: Optional[UploadFile] = None) -> MenuModel:
    """Create a new menu item."""
    try:
        if image:
            menu_data["image_url"] = await save_image(image)

        # Generate a unique ID for the menu item
        menu_id = str(uuid.uuid4())
        menu_data["id"] = menu_id
        menu_data["created_at"] = datetime.utcnow().isoformat()
        menu_data["updated_at"] = datetime.utcnow().isoformat()

        # Insert into DynamoDB
        item = {
            "Home": {"S": "Menu"},  # Partition key (must match your DynamoDB table)
            "1": {"S": menu_id},    # Sort key (must match your DynamoDB table)
            "name": {"S": menu_data.get("name", "")},
            "description": {"S": menu_data.get("description", "")},
            "category_name": {"S": menu_data.get("category_name", "")},
            "price": {"N": str(menu_data.get("price", 0.0))},
            "parcel_price": {"N": str(menu_data.get("parcel_price", 0.0))} if menu_data.get("parcel_price") is not None else {"NULL": True},
            "image_url": {"S": menu_data.get("image_url", "")},
            "is_available": {"BOOL": menu_data.get("is_available", True)},
            "is_veg": {"BOOL": menu_data.get("is_veg", True)},
            "created_at": {"S": menu_data.get("created_at", "")},
            "updated_at": {"S": menu_data.get("updated_at", "")},
        }

        await dynamodb.put_item(item)
        return MenuModel(**menu_data)

    except Exception as e:
        print(f"Error creating menu item: {e}")
        raise HTTPException(status_code=500, detail="Failed to create menu item")

async def get_menu_item(menu_id: str) -> Optional[MenuModel]:
    """Retrieve a menu item by ID."""
    try:
        key = {
            "Home": {"S": "Menu"},  # Partition key
            "1": {"S": menu_id}      # Sort key
        }
        item = await dynamodb.get_item(key)
        if item:
            # Convert DynamoDB item to MenuModel
            menu_data = {
                "id": item.get("1", {}).get("S", ""),
                "name": item.get("name", {}).get("S", ""),
                "description": item.get("description", {}).get("S", ""),
                "category_name": item.get("category_name", {}).get("S", ""),
                "price": float(item.get("price", {}).get("N", "0")),
                "parcel_price": float(item.get("parcel_price", {}).get("N", "0")) if "N" in item.get("parcel_price", {}) else None,
                "image_url": item.get("image_url", {}).get("S", ""),
                "is_available": item.get("is_available", {}).get("BOOL", True),
                "is_veg": item.get("is_veg", {}).get("BOOL", True),
                "created_at": item.get("created_at", {}).get("S", ""),
                "updated_at": item.get("updated_at", {}).get("S", ""),
            }
            return MenuModel(**menu_data)
        else:
            raise HTTPException(status_code=404, detail="Menu item not found")
    except Exception as e:
        print(f"Error retrieving menu item: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve menu item")

async def get_all_menu_items() -> List[MenuModel]:
    """Retrieve all menu items."""
    try:
        items = await dynamodb.scan()
        menu_items = []
        for item in items:
            if item.get("Home", {}).get("S") == "Menu":  # Filter by partition key
                menu_data = {
                    "id": item.get("1", {}).get("S", ""),
                    "name": item.get("name", {}).get("S", ""),
                    "description": item.get("description", {}).get("S", ""),
                    "category_name": item.get("category_name", {}).get("S", ""),
                    "price": float(item.get("price", {}).get("N", "0")),
                    "parcel_price": float(item.get("parcel_price", {}).get("N", "0")) if "N" in item.get("parcel_price", {}) else None,
                    "image_url": item.get("image_url", {}).get("S", ""),
                    "is_available": item.get("is_available", {}).get("BOOL", True),
                    "is_veg": item.get("is_veg", {}).get("BOOL", True),
                    "created_at": item.get("created_at", {}).get("S", ""),
                    "updated_at": item.get("updated_at", {}).get("S", ""),
                }
                menu_items.append(MenuModel(**menu_data))
        return menu_items
    except Exception as e:
        print(f"Error retrieving menu items: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve menu items")

async def get_menu_items_by_category(category_name: str) -> List[MenuModel]:
    """Retrieve menu items by category name."""
    try:
        items = await dynamodb.scan()
        menu_items = []
        for item in items:
            if item.get("Home", {}).get("S") == "Menu" and item.get("category_name", {}).get("S") == category_name:
                menu_data = {
                    "id": item.get("1", {}).get("S", ""),
                    "name": item.get("name", {}).get("S", ""),
                    "description": item.get("description", {}).get("S", ""),
                    "category_name": item.get("category_name", {}).get("S", ""),
                    "price": float(item.get("price", {}).get("N", "0")),
                    "parcel_price": float(item.get("parcel_price", {}).get("N", "0")) if "N" in item.get("parcel_price", {}) else None,
                    "image_url": item.get("image_url", {}).get("S", ""),
                    "is_available": item.get("is_available", {}).get("BOOL", True),
                    "is_veg": item.get("is_veg", {}).get("BOOL", True),
                    "created_at": item.get("created_at", {}).get("S", ""),
                    "updated_at": item.get("updated_at", {}).get("S", ""),
                }
                menu_items.append(MenuModel(**menu_data))
        return menu_items
    except Exception as e:
        print(f"Error retrieving menu items by category: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve menu items by category")

async def update_menu_item(menu_id: str, menu_data: dict, image: Optional[UploadFile] = None) -> Optional[MenuModel]:
    """Update a menu item."""
    try:
        if image:
            menu_data["image_url"] = await save_image(image)

        key = {
            "Home": {"S": "Menu"},  # Partition key
            "1": {"S": menu_id}      # Sort key
        }

        update_expression = "SET "
        expression_attribute_names = {}
        expression_attribute_values = {}

        # Always update updated_at
        update_expression += "#updated_at = :updated_at, "
        expression_attribute_names["#updated_at"] = "updated_at"
        expression_attribute_values[":updated_at"] = {"S": datetime.utcnow().isoformat()}

        for field, value in menu_data.items():
            if value is not None:  # Only update fields that are provided
                expression_attribute_names[f"#{field}"] = field
                
                # Handle different data types
                if field in ['price', 'parcel_price']:
                    expression_attribute_values[f":{field}"] = {"N": str(value)}
                elif field in ['is_available', 'is_veg']:
                    expression_attribute_values[f":{field}"] = {"BOOL": value}
                else:
                    expression_attribute_values[f":{field}"] = {"S": str(value)}
                
                update_expression += f"#{field} = :{field}, "

        update_expression = update_expression.rstrip(", ")

        await dynamodb.update_item(
            key=key,
            update_expression=update_expression,
            expression_attribute_names=expression_attribute_names,
            expression_attribute_values=expression_attribute_values
        )
        return await get_menu_item(menu_id)
    except Exception as e:
        print(f"Error updating menu item: {e}")
        raise HTTPException(status_code=500, detail="Failed to update menu item")

async def delete_menu_item(menu_id: str) -> bool:
    """Delete a menu item."""
    try:
        key = {
            "Home": {"S": "Menu"},  # Partition key
            "1": {"S": menu_id}      # Sort key
        }
        response = await dynamodb.delete_item(key)
        return True
    except Exception as e:
        print(f"Error deleting menu item: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete menu item")