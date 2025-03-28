# banjos_restaurant\app\services\branches_service.py
import os
import uuid
from typing import Optional
from fastapi import UploadFile, HTTPException  # Import HTTPException
from app.core.database import dynamodb
from app.models.branches import BranchModel

# Ensure static/images directory exists
os.makedirs("static/images", exist_ok=True)

async def save_image(file: UploadFile) -> str:
    """Save an uploaded image and return the file path."""
    file_path = f"static/images/{file.filename}"
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())
    return f"/{file_path}"

async def create_branch(branch_data: dict, image: Optional[UploadFile] = None) -> BranchModel:
    """Create a new branch with an optional image."""
    try:
        if image:
            branch_data["image_url"] = await save_image(image)

        # Generate a unique ID for the branch
        branch_id = str(uuid.uuid4())
        branch_data["id"] = branch_id

        # Insert into DynamoDB
        item = {
            "Home": {"S": "Branches"},  # Partition key (must match your DynamoDB table)
            "1": {"S": branch_id},      # Sort key (must match your DynamoDB table)
            "name": {"S": branch_data.get("name", "")},
            "latitude": {"N": str(branch_data.get("latitude", 0.0))},
            "longitude": {"N": str(branch_data.get("longitude", 0.0))},
            "address": {"S": branch_data.get("address", "")},
            "city": {"S": branch_data.get("city", "")},
            "state": {"S": branch_data.get("state", "")},
            "country": {"S": branch_data.get("country", "")},
            "zipcode": {"S": branch_data.get("zipcode", "")},
            "phone_number": {"S": branch_data.get("phone_number", "")},
            "email": {"S": branch_data.get("email", "")},
            "opening_hours": {"S": branch_data.get("opening_hours", "")},
            "manager_name": {"S": branch_data.get("manager_name", "")},
            "branch_opening_date": {"S": branch_data.get("branch_opening_date", "")},
            "branch_status": {"S": branch_data.get("branch_status", "open")},
            "seating_capacity": {"N": str(branch_data.get("seating_capacity", 0))},
            "parking_availability": {"BOOL": branch_data.get("parking_availability", False)},
            "wifi_availability": {"BOOL": branch_data.get("wifi_availability", False)},
            "image_url": {"S": branch_data.get("image_url", "")}
        }

        await dynamodb.put_item(item)
        return BranchModel(**branch_data)

    except Exception as e:
        print(f"Error creating branch: {e}")
        raise HTTPException(status_code=500, detail="Failed to create branch")

async def get_branch(branch_id: str) -> Optional[BranchModel]:
    """Retrieve a branch by ID."""
    try:
        key = {
            "Home": {"S": "Branches"},  # Partition key
            "1": {"S": branch_id}       # Sort key
        }
        item = await dynamodb.get_item(key)
        if item:
            # Convert DynamoDB item to BranchModel
            branch_data = {
                "id": item.get("1", {}).get("S", ""),  # Use the sort key as the id
                "name": item.get("name", {}).get("S", ""),
                "latitude": float(item.get("latitude", {}).get("N", "0")),
                "longitude": float(item.get("longitude", {}).get("N", "0")),
                "address": item.get("address", {}).get("S", ""),
                "city": item.get("city", {}).get("S", ""),
                "state": item.get("state", {}).get("S", ""),
                "country": item.get("country", {}).get("S", ""),
                "zipcode": item.get("zipcode", {}).get("S", ""),
                "phone_number": item.get("phone_number", {}).get("S", ""),
                "email": item.get("email", {}).get("S", ""),
                "opening_hours": item.get("opening_hours", {}).get("S", ""),
                "manager_name": item.get("manager_name", {}).get("S", ""),
                "branch_opening_date": item.get("branch_opening_date", {}).get("S", ""),
                "branch_status": item.get("branch_status", {}).get("S", "open"),
                "seating_capacity": int(item.get("seating_capacity", {}).get("N", "0")),
                "parking_availability": item.get("parking_availability", {}).get("BOOL", False),
                "wifi_availability": item.get("wifi_availability", {}).get("BOOL", False),
                "image_url": item.get("image_url", {}).get("S", "")
            }
            return BranchModel(**branch_data)
        else:
            raise HTTPException(status_code=404, detail="Branch not found")
    except Exception as e:
        print(f"Error retrieving branch: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve branch")

async def get_all_branches() -> list[BranchModel]:
    """Retrieve all branches."""
    try:
        items = await dynamodb.scan()
        branches = []
        for item in items:
            if item.get("Home", {}).get("S") == "Branches":  # Filter by partition key
                branch_data = {
                    "id": item.get("1", {}).get("S", ""),  # Use the sort key as the id
                    "name": item.get("name", {}).get("S", ""),
                    "latitude": float(item.get("latitude", {}).get("N", "0")),
                    "longitude": float(item.get("longitude", {}).get("N", "0")),
                    "address": item.get("address", {}).get("S", ""),
                    "city": item.get("city", {}).get("S", ""),
                    "state": item.get("state", {}).get("S", ""),
                    "country": item.get("country", {}).get("S", ""),
                    "zipcode": item.get("zipcode", {}).get("S", ""),
                    "phone_number": item.get("phone_number", {}).get("S", ""),
                    "email": item.get("email", {}).get("S", ""),
                    "opening_hours": item.get("opening_hours", {}).get("S", ""),
                    "manager_name": item.get("manager_name", {}).get("S", ""),
                    "branch_opening_date": item.get("branch_opening_date", {}).get("S", ""),
                    "branch_status": item.get("branch_status", {}).get("S", "open"),
                    "seating_capacity": int(item.get("seating_capacity", {}).get("N", "0")),
                    "parking_availability": item.get("parking_availability", {}).get("BOOL", False),
                    "wifi_availability": item.get("wifi_availability", {}).get("BOOL", False),
                    "image_url": item.get("image_url", {}).get("S", "")
                }
                branches.append(BranchModel(**branch_data))
        return branches
    except Exception as e:
        print(f"Error retrieving branches: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve branches")

async def update_branch(branch_id: str, branch_data: dict, image: Optional[UploadFile] = None) -> Optional[BranchModel]:
    """Update a branch."""
    try:
        if image:
            branch_data["image_url"] = await save_image(image)

        key = {
            "Home": {"S": "Branches"},  # Partition key
            "1": {"S": branch_id}       # Sort key
        }

        update_expression = "SET "
        expression_attribute_names = {}
        expression_attribute_values = {}

        for field, value in branch_data.items():
            if value is not None:  # Only update fields that are provided
                expression_attribute_names[f"#{field}"] = field
                update_expression += f"#{field} = :{field}, "
                
                # Handle different data types appropriately
                if field in ["latitude", "longitude", "seating_capacity"]:
                    expression_attribute_values[f":{field}"] = {"N": str(value)}
                elif field in ["parking_availability", "wifi_availability"]:
                    expression_attribute_values[f":{field}"] = {"BOOL": bool(value)}
                else:
                    expression_attribute_values[f":{field}"] = {"S": str(value)}

        update_expression = update_expression.rstrip(", ")

        await dynamodb.update_item(
            key=key,
            update_expression=update_expression,
            expression_attribute_names=expression_attribute_names,
            expression_attribute_values=expression_attribute_values
        )
        return await get_branch(branch_id)
    except Exception as e:
        print(f"Error updating branch: {e}")
        raise HTTPException(status_code=500, detail="Failed to update branch")
    
async def delete_branch(branch_id: str) -> bool:
    """Delete a branch."""
    try:
        key = {
            "Home": {"S": "Branches"},  # Partition key
            "1": {"S": branch_id}       # Sort key
        }
        response = await dynamodb.delete_item(key)
        return True
    except Exception as e:
        print(f"Error deleting branch: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete branch")