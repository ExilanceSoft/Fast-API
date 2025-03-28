import os
import uuid
from typing import Optional, List
from fastapi import HTTPException, UploadFile, status
from app.core.database import dynamodb
from app.schemas.job_applications import (
    JobApplicationCreate, 
    JobApplicationResponse, 
    ALLOWED_STATUSES,
    ApplicationStatus
)
from datetime import datetime
from app.utils.email import send_email

os.makedirs("static/resumes", exist_ok=True)

async def save_resume(file: UploadFile) -> str:
    """Save an uploaded resume and return the file path."""
    unique_filename = f"{uuid.uuid4()}_{file.filename}"
    file_path = f"static/resumes/{unique_filename}"
    with open(file_path, "wb") as buffer:
        buffer.write(await file.read())
    return f"/{file_path}"

async def create_job_application(
    application_data: JobApplicationCreate, 
    resume: Optional[UploadFile] = None
) -> JobApplicationResponse:
    """Create a new job application."""
    try:
        if resume:
            application_data.resume_url = await save_resume(resume)
        else:
            application_data.resume_url = ""

        application_id = str(uuid.uuid4())
        created_at = updated_at = datetime.utcnow().isoformat()

        item = {
            "Home": {"S": "JobApplications"},
            "1": {"S": application_id},
            "full_name": {"S": application_data.full_name},
            "email": {"S": application_data.email},
            "phone": {"S": application_data.phone},
            "address": {"S": application_data.address or ""},
            "job_position_id": {"S": application_data.job_position_id},
            "job_position_title": {"S": application_data.job_position_title},
            "experience": {"S": application_data.experience or ""},
            "skills": {"S": application_data.skills or ""},
            "cover_letter": {"S": application_data.cover_letter or ""},
            "resume_url": {"S": application_data.resume_url},
            "status": {"S": application_data.status},
            "created_at": {"S": created_at},
            "updated_at": {"S": updated_at},
        }

        await dynamodb.put_item(item)

        email_context = {
            'applicant_name': application_data.full_name,
            'position_title': application_data.job_position_title
        }
        
        send_email(
            recipient=application_data.email,
            subject="Job Application Received",
            template_name="job_application_confirmation.html",
            context=email_context
        )

        response_data = application_data.model_dump()
        response_data.update({
            "id": application_id,
            "created_at": created_at,
            "updated_at": updated_at,
            "resume_url": application_data.resume_url
        })
        return JobApplicationResponse(**response_data)

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create job application: {str(e)}"
        )

async def get_all_job_applications() -> List[JobApplicationResponse]:
    """Retrieve all job applications."""
    try:
        items = await dynamodb.scan()
        applications = []
        for item in items:
            if item.get("Home", {}).get("S") == "JobApplications":
                application_data = {
                    "id": item.get("1", {}).get("S", ""),
                    "full_name": item.get("full_name", {}).get("S", ""),
                    "email": item.get("email", {}).get("S", ""),
                    "phone": item.get("phone", {}).get("S", ""),
                    "address": item.get("address", {}).get("S", ""),
                    "job_position_id": item.get("job_position_id", {}).get("S", ""),
                    "job_position_title": item.get("job_position_title", {}).get("S", ""),
                    "experience": item.get("experience", {}).get("S", ""),
                    "skills": item.get("skills", {}).get("S", ""),
                    "cover_letter": item.get("cover_letter", {}).get("S", ""),
                    "resume_url": item.get("resume_url", {}).get("S", ""),
                    "status": item.get("status", {}).get("S", ApplicationStatus.PENDING.value),
                    "created_at": item.get("created_at", {}).get("S", ""),
                    "updated_at": item.get("updated_at", {}).get("S", ""),
                }
                try:
                    applications.append(JobApplicationResponse(**application_data))
                except ValueError as e:
                    application_data['status'] = ApplicationStatus.PENDING.value
                    applications.append(JobApplicationResponse(**application_data))
        return applications
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve job applications: {str(e)}"
        )

async def get_job_application_by_id(application_id: str) -> Optional[JobApplicationResponse]:
    """Retrieve a job application by ID."""
    try:
        key = {
            "Home": {"S": "JobApplications"},
            "1": {"S": application_id}
        }
        item = await dynamodb.get_item(key)
        if not item:
            return None
            
        application_data = {
            "id": item.get("1", {}).get("S", ""),
            "full_name": item.get("full_name", {}).get("S", ""),
            "email": item.get("email", {}).get("S", ""),
            "phone": item.get("phone", {}).get("S", ""),
            "address": item.get("address", {}).get("S", ""),
            "job_position_id": item.get("job_position_id", {}).get("S", ""),
            "job_position_title": item.get("job_position_title", {}).get("S", ""),
            "experience": item.get("experience", {}).get("S", ""),
            "skills": item.get("skills", {}).get("S", ""),
            "cover_letter": item.get("cover_letter", {}).get("S", ""),
            "resume_url": item.get("resume_url", {}).get("S", ""),
            "status": item.get("status", {}).get("S", ApplicationStatus.PENDING.value),
            "created_at": item.get("created_at", {}).get("S", ""),
            "updated_at": item.get("updated_at", {}).get("S", ""),
        }
        
        try:
            return JobApplicationResponse(**application_data)
        except ValueError as e:
            application_data['status'] = ApplicationStatus.PENDING.value
            return JobApplicationResponse(**application_data)
            
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve job application: {str(e)}"
        )

async def update_job_application_status(
    application_id: str, 
    new_status: str
) -> Optional[JobApplicationResponse]:
    """Update the status of a job application."""
    try:
        application = await get_job_application_by_id(application_id)
        if not application:
            return None

        key = {
            "Home": {"S": "JobApplications"},
            "1": {"S": application_id}
        }

        updated_at = datetime.utcnow().isoformat()

        update_expression = "SET #status = :status, #updated_at = :updated_at"
        expression_attribute_names = {
            "#status": "status",
            "#updated_at": "updated_at"
        }
        expression_attribute_values = {
            ":status": {"S": new_status},
            ":updated_at": {"S": updated_at}
        }

        await dynamodb.update_item(
            key=key,
            update_expression=update_expression,
            expression_attribute_names=expression_attribute_names,
            expression_attribute_values=expression_attribute_values
        )

        email_context = {
            'applicant_name': application.full_name,
            'status': new_status,
            'position_title': application.job_position_title
        }
        
        send_email(
            recipient=application.email,
            subject="Your Application Status Update",
            template_name="job_application_status_update.html",
            context=email_context
        )

        application.status = new_status
        application.updated_at = updated_at
        return application

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update job application status: {str(e)}"
        )

async def delete_job_application(application_id: str) -> bool:
    """Delete a job application."""
    try:
        key = {
            "Home": {"S": "JobApplications"},
            "1": {"S": application_id}
        }
        await dynamodb.delete_item(key)
        return True
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete job application: {str(e)}"
        )

async def filter_job_applications_by_title(job_title: str) -> List[JobApplicationResponse]:
    """Filter job applications by job title."""
    try:
        if not job_title.strip():
            return []
            
        all_applications = await get_all_job_applications()
        return [
            app for app in all_applications 
            if job_title.lower() in app.job_position_title.lower()
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to filter job applications: {str(e)}"
        )