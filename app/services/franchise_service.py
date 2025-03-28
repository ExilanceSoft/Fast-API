import uuid
from fastapi import HTTPException
from app.core.database import dynamodb
from app.models.franchise import FranchiseRequestCreate, FranchiseRequestResponse
from datetime import datetime
from typing import Optional, List
from app.utils.email import send_email

async def create_franchise_request(request_data: FranchiseRequestCreate) -> FranchiseRequestResponse:
    """Create a new franchise request."""
    try:
        request_id = str(uuid.uuid4())
        created_at = datetime.utcnow()
        updated_at = created_at

        item = {
            "Home": {"S": "FranchiseRequests"},
            "1": {"S": request_id},
            "user_name": {"S": request_data.user_name},
            "user_email": {"S": request_data.user_email},
            "user_phone": {"S": request_data.user_phone},
            "requested_city": {"S": request_data.requested_city},
            "requested_state": {"S": request_data.requested_state or ""},
            "requested_country": {"S": request_data.requested_country},
            "investment_budget": {"N": str(request_data.investment_budget)},
            "experience_in_food_business": {"S": request_data.experience_in_food_business or ""},
            "additional_details": {"S": request_data.additional_details or ""},
            "request_status": {"S": request_data.request_status},
            "created_at": {"S": created_at.isoformat()},
            "updated_at": {"S": updated_at.isoformat()},
        }

        await dynamodb.put_item(item)
        
        # Send confirmation email
        email_context = {
            "user_name": request_data.user_name,
            "request_id": request_id,
            "requested_city": request_data.requested_city,
            "requested_state": request_data.requested_state or "",
            "requested_country": request_data.requested_country,
            "investment_budget": request_data.investment_budget,
            "request_status": request_data.request_status
        }
        
        send_email(
            recipient=request_data.user_email,
            subject="Your Banjo's Restaurant Franchise Request Has Been Received",
            template_name="franchise_request_created.html",
            context=email_context
        )

        return FranchiseRequestResponse(
            id=request_id,
            created_at=created_at,
            updated_at=updated_at,
            **request_data.dict()
        )

    except Exception as e:
        print(f"Error creating franchise request: {e}")
        raise HTTPException(status_code=500, detail="Failed to create franchise request")


async def get_all_requests() -> List[FranchiseRequestResponse]:
    """Retrieve all franchise requests."""
    try:
        items = await dynamodb.scan()
        requests = []
        for item in items:
            if item.get("Home", {}).get("S") == "FranchiseRequests":  # Filter by partition key
                request_data = {
                    "id": item.get("1", {}).get("S", ""),
                    "user_name": item.get("user_name", {}).get("S", ""),
                    "user_email": item.get("user_email", {}).get("S", ""),
                    "user_phone": item.get("user_phone", {}).get("S", ""),
                    "requested_city": item.get("requested_city", {}).get("S", ""),
                    "requested_state": item.get("requested_state", {}).get("S", ""),
                    "requested_country": item.get("requested_country", {}).get("S", ""),
                    "investment_budget": float(item.get("investment_budget", {}).get("N", "0")),
                    "experience_in_food_business": item.get("experience_in_food_business", {}).get("S", ""),
                    "additional_details": item.get("additional_details", {}).get("S", ""),
                    "request_status": item.get("request_status", {}).get("S", "pending"),
                    "created_at": datetime.fromisoformat(item.get("created_at", {}).get("S", "")),
                    "updated_at": datetime.fromisoformat(item.get("updated_at", {}).get("S", "")),
                }
                requests.append(FranchiseRequestResponse(**request_data))
        return requests
    except Exception as e:
        print(f"Error retrieving franchise requests: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve franchise requests")

async def get_request_by_id(request_id: str) -> Optional[FranchiseRequestResponse]:
    """Retrieve a franchise request by ID."""
    try:
        key = {
            "Home": {"S": "FranchiseRequests"},  # Partition key
            "1": {"S": request_id}              # Sort key
        }
        item = await dynamodb.get_item(key)
        if item:
            request_data = {
                "id": item.get("1", {}).get("S", ""),
                "user_name": item.get("user_name", {}).get("S", ""),
                "user_email": item.get("user_email", {}).get("S", ""),
                "user_phone": item.get("user_phone", {}).get("S", ""),
                "requested_city": item.get("requested_city", {}).get("S", ""),
                "requested_state": item.get("requested_state", {}).get("S", ""),
                "requested_country": item.get("requested_country", {}).get("S", ""),
                "investment_budget": float(item.get("investment_budget", {}).get("N", "0")),
                "experience_in_food_business": item.get("experience_in_food_business", {}).get("S", ""),
                "additional_details": item.get("additional_details", {}).get("S", ""),
                "request_status": item.get("request_status", {}).get("S", "pending"),
                "created_at": datetime.fromisoformat(item.get("created_at", {}).get("S", "")),
                "updated_at": datetime.fromisoformat(item.get("updated_at", {}).get("S", "")),
            }
            return FranchiseRequestResponse(**request_data)
        else:
            raise HTTPException(status_code=404, detail="Franchise request not found")
    except Exception as e:
        print(f"Error retrieving franchise request: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve franchise request")

async def update_request_status(request_id: str, status: str) -> Optional[FranchiseRequestResponse]:
    """Update a franchise request status."""
    try:
        # First get the current request to get user details
        current_request = await get_request_by_id(request_id)
        if not current_request:
            raise HTTPException(status_code=404, detail="Franchise request not found")

        key = {
            "Home": {"S": "FranchiseRequests"},
            "1": {"S": request_id}
        }

        update_expression = "SET #request_status = :status, #updated_at = :updated_at"
        expression_attribute_names = {
            "#request_status": "request_status",
            "#updated_at": "updated_at"
        }
        expression_attribute_values = {
            ":status": {"S": status},
            ":updated_at": {"S": datetime.utcnow().isoformat()}
        }

        await dynamodb.update_item(
            key=key,
            update_expression=update_expression,
            expression_attribute_names=expression_attribute_names,
            expression_attribute_values=expression_attribute_values
        )
        
        # Send status update email
        email_context = {
            "user_name": current_request.user_name,
            "request_id": request_id,
            "requested_city": current_request.requested_city,
            "requested_state": current_request.requested_state or "",
            "requested_country": current_request.requested_country,
            "request_status": status
        }
        
        send_email(
            recipient=current_request.user_email,
            subject=f"Your Banjo's Franchise Request Status Update: {status.capitalize()}",
            template_name="franchise_status_updated.html",
            context=email_context
        )

        return await get_request_by_id(request_id)
    except Exception as e:
        print(f"Error updating franchise request: {e}")
        raise HTTPException(status_code=500, detail="Failed to update franchise request")
    
async def delete_request(request_id: str) -> bool:
    """Delete a franchise request."""
    try:
        key = {
            "Home": {"S": "FranchiseRequests"},  # Partition key
            "1": {"S": request_id}              # Sort key
        }
        await dynamodb.delete_item(key)
        return True
    except Exception as e:
        print(f"Error deleting franchise request: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete franchise request")