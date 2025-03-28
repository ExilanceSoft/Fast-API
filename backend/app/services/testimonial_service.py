from app.core.database import dynamodb
from app.models.testimonial import Testimonial
from app.utils.email import send_email
from datetime import datetime
from fastapi import HTTPException
import uuid

async def create_testimonial(testimonial_data: dict):
    """Create a new testimonial."""
    try:
        # Generate a unique ID for the testimonial
        testimonial_id = str(uuid.uuid4())
        testimonial_data["id"] = testimonial_id
        testimonial_data["created_at"] = datetime.utcnow().isoformat()
        testimonial_data["status"] = "pending"  # Default status

        # Insert testimonial into DynamoDB
        item = {
            "Home": {"S": "Testimonials"},  # Partition key
            "1": {"S": testimonial_id},     # Sort key
            "name": {"S": testimonial_data["name"]},
            "email": {"S": testimonial_data["email"]},
            "description": {"S": testimonial_data["description"]},
            "rating": {"N": str(testimonial_data["rating"])},
            "status": {"S": testimonial_data["status"]},
            "created_at": {"S": testimonial_data["created_at"]}
        }

        # Add image if provided
        if "image" in testimonial_data:
            item["image"] = {"S": testimonial_data["image"]}

        await dynamodb.put_item(item)

        # Send confirmation email to the user
        send_email(
            recipient=testimonial_data["email"],
            subject="Thank you for your testimonial!",
            template_name="testimonial_confirmation.html",
            context={"name": testimonial_data["name"]}
        )

        return testimonial_id
    except Exception as e:
        print(f"Error creating testimonial: {e}")
        raise HTTPException(status_code=500, detail="Failed to create testimonial")

async def get_testimonial(testimonial_id: str):
    """Retrieve a testimonial by ID."""
    try:
        key = {
            "Home": {"S": "Testimonials"},  # Partition key
            "1": {"S": testimonial_id}      # Sort key
        }
        item = await dynamodb.get_item(key)
        if item:
            testimonial_data = {
                "id": item.get("1", {}).get("S", ""),
                "name": item.get("name", {}).get("S", ""),
                "email": item.get("email", {}).get("S", ""),
                "description": item.get("description", {}).get("S", ""),
                "rating": int(item.get("rating", {}).get("N", "0")),
                "status": item.get("status", {}).get("S", ""),
                "created_at": item.get("created_at", {}).get("S", "")
            }
            if "image" in item:
                testimonial_data["image"] = item.get("image", {}).get("S", "")
            return testimonial_data
        return None
    except Exception as e:
        print(f"Error retrieving testimonial: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve testimonial")

async def get_all_testimonials():
    """Retrieve all testimonials."""
    try:
        items = await dynamodb.scan()
        testimonials = []
        for item in items:
            if item.get("Home", {}).get("S") == "Testimonials":  # Filter by partition key
                testimonial_data = {
                    "id": item.get("1", {}).get("S", ""),
                    "name": item.get("name", {}).get("S", ""),
                    "email": item.get("email", {}).get("S", ""),
                    "description": item.get("description", {}).get("S", ""),
                    "rating": int(item.get("rating", {}).get("N", "0")),
                    "status": item.get("status", {}).get("S", ""),
                    "created_at": item.get("created_at", {}).get("S", "")
                }
                if "image" in item:
                    testimonial_data["image"] = item.get("image", {}).get("S", "")
                testimonials.append(testimonial_data)
        return testimonials
    except Exception as e:
        print(f"Error retrieving testimonials: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve testimonials")

async def update_testimonial_status(testimonial_id: str, status: str):
    """Update the status of a testimonial."""
    try:
        key = {
            "Home": {"S": "Testimonials"},  # Partition key
            "1": {"S": testimonial_id}      # Sort key
        }

        update_expression = "SET #status = :status"
        expression_attribute_names = {"#status": "status"}
        expression_attribute_values = {":status": {"S": status}}

        await dynamodb.update_item(
            key=key,
            update_expression=update_expression,
            expression_attribute_names=expression_attribute_names,
            expression_attribute_values=expression_attribute_values
        )
    except Exception as e:
        print(f"Error updating testimonial status: {e}")
        raise HTTPException(status_code=500, detail="Failed to update testimonial status")

async def delete_testimonial(testimonial_id: str):
    """Delete a testimonial by ID."""
    try:
        key = {
            "Home": {"S": "Testimonials"},
            "1": {"S": testimonial_id}
        }
        await dynamodb.delete_item(key)
    except Exception as e:
        print(f"Error deleting testimonial: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete testimonial")