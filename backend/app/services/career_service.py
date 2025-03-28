# banjos_restaurant\app\services\career_service.py
import uuid
from datetime import datetime
from fastapi import HTTPException
from app.core.database import dynamodb
from app.models.career import JobApplicationModel

async def apply_for_job(application_data: dict) -> JobApplicationModel:
    """Submit a job application."""
    try:
        # Generate a unique ID for the application
        application_id = str(uuid.uuid4())
        application_data["id"] = application_id
        application_data["created_at"] = datetime.utcnow().isoformat()
        application_data["updated_at"] = datetime.utcnow().isoformat()
        application_data["application_status"] = "pending"

        # Insert into DynamoDB
        item = {
            "Home": {"S": "JobApplications"},  # Partition key
            "1": {"S": application_id},       # Sort key
            "branch_id": {"S": application_data.get("branch_id", "")},
            "job_title": {"S": application_data.get("job_title", "")},
            "applicant_name": {"S": application_data.get("applicant_name", "")},
            "applicant_email": {"S": application_data.get("applicant_email", "")},
            "applicant_phone": {"S": application_data.get("applicant_phone", "")},
            "resume_url": {"S": application_data.get("resume_url", "")},
            "cover_letter": {"S": application_data.get("cover_letter", "")},
            "application_status": {"S": application_data.get("application_status", "pending")},
            "created_at": {"S": application_data.get("created_at", "")},
            "updated_at": {"S": application_data.get("updated_at", "")}
        }

        await dynamodb.put_item(item)
        return JobApplicationModel(**application_data)

    except Exception as e:
        print(f"Error submitting job application: {e}")
        raise HTTPException(status_code=500, detail="Failed to submit job application")

async def get_all_applications() -> list[JobApplicationModel]:
    """Retrieve all job applications."""
    try:
        items = await dynamodb.scan()
        applications = []
        for item in items:
            if item.get("Home", {}).get("S") == "JobApplications":  # Filter by partition key
                application_data = {
                    "id": item.get("1", {}).get("S", ""),  # Use the sort key as the id
                    "branch_id": item.get("branch_id", {}).get("S", ""),
                    "job_title": item.get("job_title", {}).get("S", ""),
                    "applicant_name": item.get("applicant_name", {}).get("S", ""),
                    "applicant_email": item.get("applicant_email", {}).get("S", ""),
                    "applicant_phone": item.get("applicant_phone", {}).get("S", ""),
                    "resume_url": item.get("resume_url", {}).get("S", ""),
                    "cover_letter": item.get("cover_letter", {}).get("S", ""),
                    "application_status": item.get("application_status", {}).get("S", "pending"),
                    "created_at": item.get("created_at", {}).get("S", ""),
                    "updated_at": item.get("updated_at", {}).get("S", "")
                }
                applications.append(JobApplicationModel(**application_data))
        return applications
    except Exception as e:
        print(f"Error retrieving job applications: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve job applications")

async def get_application_by_id(application_id: str) -> Optional[JobApplicationModel]:
    """Retrieve a job application by ID."""
    try:
        key = {
            "Home": {"S": "JobApplications"},  # Partition key
            "1": {"S": application_id}         # Sort key
        }
        item = await dynamodb.get_item(key)
        if item:
            application_data = {
                "id": item.get("1", {}).get("S", ""),  # Use the sort key as the id
                "branch_id": item.get("branch_id", {}).get("S", ""),
                "job_title": item.get("job_title", {}).get("S", ""),
                "applicant_name": item.get("applicant_name", {}).get("S", ""),
                "applicant_email": item.get("applicant_email", {}).get("S", ""),
                "applicant_phone": item.get("applicant_phone", {}).get("S", ""),
                "resume_url": item.get("resume_url", {}).get("S", ""),
                "cover_letter": item.get("cover_letter", {}).get("S", ""),
                "application_status": item.get("application_status", {}).get("S", "pending"),
                "created_at": item.get("created_at", {}).get("S", ""),
                "updated_at": item.get("updated_at", {}).get("S", "")
            }
            return JobApplicationModel(**application_data)
        else:
            raise HTTPException(status_code=404, detail="Job application not found")
    except Exception as e:
        print(f"Error retrieving job application: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve job application")

async def update_application_status(application_id: str, status: str) -> Optional[JobApplicationModel]:
    """Update the status of a job application."""
    try:
        key = {
            "Home": {"S": "JobApplications"},  # Partition key
            "1": {"S": application_id}         # Sort key
        }

        update_expression = "SET application_status = :status, updated_at = :updated_at"
        expression_attribute_values = {
            ":status": {"S": status},
            ":updated_at": {"S": datetime.utcnow().isoformat()}
        }

        await dynamodb.update_item(
            key=key,
            update_expression=update_expression,
            expression_attribute_values=expression_attribute_values
        )
        return await get_application_by_id(application_id)
    except Exception as e:
        print(f"Error updating job application status: {e}")
        raise HTTPException(status_code=500, detail="Failed to update job application status")