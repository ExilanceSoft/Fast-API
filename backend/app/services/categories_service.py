# banjos_restaurant\app\services\categories_service.py
import os
import uuid
from typing import Optional, List
from fastapi import HTTPException
from app.core.database import dynamodb
from app.models.categories import CategoryModel

async def create_category(category_data: dict) -> CategoryModel:
    """Create a new category."""
    try:
        # Generate a unique ID for the category
        category_id = str(uuid.uuid4())
        category_data["id"] = category_id

        # Insert into DynamoDB
        item = {
            "Home": {"S": "Categories"},  # Partition key (must match your DynamoDB table)
            "1": {"S": category_id},      # Sort key (must match your DynamoDB table)
            "name": {"S": category_data.get("name", "")},
        }

        await dynamodb.put_item(item)
        return CategoryModel(**category_data)

    except Exception as e:
        print(f"Error creating category: {e}")
        raise HTTPException(status_code=500, detail="Failed to create category")

async def get_category(category_id: str) -> Optional[CategoryModel]:
    """Retrieve a category by ID."""
    try:
        key = {
            "Home": {"S": "Categories"},  # Partition key
            "1": {"S": category_id}       # Sort key
        }
        item = await dynamodb.get_item(key)
        if item:
            # Convert DynamoDB item to CategoryModel
            category_data = {
                "id": item.get("1", {}).get("S", ""),  # Use the sort key as the id
                "name": item.get("name", {}).get("S", ""),
            }
            return CategoryModel(**category_data)
        else:
            raise HTTPException(status_code=404, detail="Category not found")
    except Exception as e:
        print(f"Error retrieving category: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve category")

async def get_all_categories() -> List[CategoryModel]:
    """Retrieve all categories."""
    try:
        items = await dynamodb.scan()
        categories = []
        for item in items:
            if item.get("Home", {}).get("S") == "Categories":  # Filter by partition key
                category_data = {
                    "id": item.get("1", {}).get("S", ""),  # Use the sort key as the id
                    "name": item.get("name", {}).get("S", ""),
                }
                categories.append(CategoryModel(**category_data))
        return categories
    except Exception as e:
        print(f"Error retrieving categories: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve categories")

async def update_category(category_id: str, category_data: dict) -> Optional[CategoryModel]:
    """Update a category."""
    try:
        key = {
            "Home": {"S": "Categories"},  # Partition key
            "1": {"S": category_id}       # Sort key
        }

        update_expression = "SET "
        expression_attribute_names = {}
        expression_attribute_values = {}

        for field, value in category_data.items():
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
        return await get_category(category_id)
    except Exception as e:
        print(f"Error updating category: {e}")
        raise HTTPException(status_code=500, detail="Failed to update category")

async def delete_category(category_id: str) -> bool:
    """Delete a category."""
    try:
        key = {
            "Home": {"S": "Categories"},  # Partition key
            "1": {"S": category_id}       # Sort key
        }
        response = await dynamodb.delete_item(key)
        return True
    except Exception as e:
        print(f"Error deleting category: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete category")