import os
import uuid
from typing import Optional, List
from fastapi import HTTPException, UploadFile
from app.core.database import dynamodb
from app.schemas.job_position import JobPositionCreate, JobPositionResponse
from datetime import datetime

# Ensure static/images directory exists
os.makedirs("static/images", exist_ok=True)

async def save_image(file: UploadFile) -> str:
    """Save an uploaded image and return the file path."""
    file_extension = os.path.splitext(file.filename)[1]
    file_name = f"{uuid.uuid4()}{file_extension}"
    file_path = f"static/images/{file_name}"
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())
    return f"/{file_path}"

async def create_job_position(job_data: dict, image: Optional[UploadFile] = None) -> JobPositionResponse:
    """Create a new job position."""
    try:
        if image:
            job_data["image_url"] = await save_image(image)

        # Generate a unique ID for the job position
        job_id = str(uuid.uuid4())
        job_data["id"] = job_id
        job_data["created_at"] = datetime.utcnow().isoformat()
        job_data["updated_at"] = datetime.utcnow().isoformat()

        # Insert into DynamoDB
        item = {
            "Home": {"S": "JobPositions"},
            "1": {"S": job_id},
            "title": {"S": job_data.get("title", "")},
            "description": {"S": job_data.get("description", "")},
            "min_salary": {"N": str(job_data.get("min_salary", 0.0))},
            "max_salary": {"N": str(job_data.get("max_salary", 0.0))},
            "branch_name": {"S": job_data.get("branch_name", "")},
            "job_type": {"S": job_data.get("job_type", "")},
            "status": {"S": job_data.get("status", "active")},
            "image_url": {"S": job_data.get("image_url", "")},
            "created_at": {"S": job_data["created_at"]},
            "updated_at": {"S": job_data["updated_at"]},
        }

        await dynamodb.put_item(item)
        return JobPositionResponse(**job_data)

    except Exception as e:
        print(f"Error creating job position: {e}")
        raise HTTPException(status_code=500, detail="Failed to create job position")

async def get_all_job_positions() -> List[JobPositionResponse]:
    """Retrieve all job positions."""
    try:
        items = await dynamodb.scan()
        jobs = []
        for item in items:
            if item.get("Home", {}).get("S") == "JobPositions":
                jobs.append({
                    "id": item.get("1", {}).get("S", ""),
                    "title": item.get("title", {}).get("S", ""),
                    "description": item.get("description", {}).get("S", ""),
                    "min_salary": float(item.get("min_salary", {}).get("N", "0")),
                    "max_salary": float(item.get("max_salary", {}).get("N", "0")),
                    "branch_name": item.get("branch_name", {}).get("S", ""),
                    "job_type": item.get("job_type", {}).get("S", ""),
                    "status": item.get("status", {}).get("S", "active"),
                    "image_url": item.get("image_url", {}).get("S", ""),
                    "created_at": item.get("created_at", {}).get("S", ""),
                    "updated_at": item.get("updated_at", {}).get("S", ""),
                })
        return jobs
    except Exception as e:
        print(f"Error retrieving job positions: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve job positions")

async def get_job_position_by_id(job_id: str) -> Optional[JobPositionResponse]:
    """Retrieve a job position by ID."""
    try:
        key = {
            "Home": {"S": "JobPositions"},
            "1": {"S": job_id}
        }
        item = await dynamodb.get_item(key)
        if item:
            return {
                "id": item.get("1", {}).get("S", ""),
                "title": item.get("title", {}).get("S", ""),
                "description": item.get("description", {}).get("S", ""),
                "min_salary": float(item.get("min_salary", {}).get("N", "0")),
                "max_salary": float(item.get("max_salary", {}).get("N", "0")),
                "branch_name": item.get("branch_name", {}).get("S", ""),
                "job_type": item.get("job_type", {}).get("S", ""),
                "status": item.get("status", {}).get("S", "active"),
                "image_url": item.get("image_url", {}).get("S", ""),
                "created_at": item.get("created_at", {}).get("S", ""),
                "updated_at": item.get("updated_at", {}).get("S", ""),
            }
        else:
            raise HTTPException(status_code=404, detail="Job position not found")
    except Exception as e:
        print(f"Error retrieving job position: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve job position")

async def update_job_position(job_id: str, job_data: dict, image: Optional[UploadFile] = None) -> Optional[JobPositionResponse]:
    """Update a job position."""
    try:
        # Get existing job data first
        existing_job = await get_job_position_by_id(job_id)
        if not existing_job:
            raise HTTPException(status_code=404, detail="Job position not found")

        # Handle image update
        if image:
            job_data["image_url"] = await save_image(image)
        elif "image_url" not in job_data and existing_job.get("image_url"):
            # Keep existing image if no new image provided
            job_data["image_url"] = existing_job["image_url"]

        key = {
            "Home": {"S": "JobPositions"},
            "1": {"S": job_id}
        }

        update_expression = "SET title = :title, description = :description, " \
                           "min_salary = :min_salary, max_salary = :max_salary, " \
                           "branch_name = :branch_name, job_type = :job_type, " \
                           "#st = :status, image_url = :image_url, updated_at = :updated_at"
        
        expression_attribute_values = {
            ":title": {"S": job_data.get("title", existing_job.get("title", ""))},
            ":description": {"S": job_data.get("description", existing_job.get("description", ""))},
            ":min_salary": {"N": str(job_data.get("min_salary", existing_job.get("min_salary", 0.0)))},
            ":max_salary": {"N": str(job_data.get("max_salary", existing_job.get("max_salary", 0.0)))},
            ":branch_name": {"S": job_data.get("branch_name", existing_job.get("branch_name", ""))},
            ":job_type": {"S": job_data.get("job_type", existing_job.get("job_type", ""))},
            ":status": {"S": job_data.get("status", existing_job.get("status", "active"))},
            ":image_url": {"S": job_data.get("image_url", existing_job.get("image_url", ""))},
            ":updated_at": {"S": datetime.utcnow().isoformat()}
        }

        expression_attribute_names = {
            "#st": "status"
        }

        await dynamodb.update_item(
            key=key,
            update_expression=update_expression,
            expression_attribute_values=expression_attribute_values,
            expression_attribute_names=expression_attribute_names
        )

        return await get_job_position_by_id(job_id)
    except Exception as e:
        print(f"Error updating job position: {e}")
        raise HTTPException(status_code=500, detail="Failed to update job position")

async def delete_job_position(job_id: str) -> bool:
    """Delete a job position."""
    try:
        key = {
            "Home": {"S": "JobPositions"},
            "1": {"S": job_id}
        }
        await dynamodb.delete_item(key)
        return True
    except Exception as e:
        print(f"Error deleting job position: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete job position")