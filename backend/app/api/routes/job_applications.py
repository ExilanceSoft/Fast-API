from fastapi import APIRouter, UploadFile, File, HTTPException, Form, Depends
from typing import Optional, List
from datetime import datetime
from app.schemas.job_applications import JobApplicationCreate, JobApplicationResponse, ALLOWED_STATUSES, StatusUpdate
from app.services.job_applications_service import (
    create_job_application,
    get_all_job_applications,
    get_job_application_by_id,
    update_job_application_status,
    delete_job_application,
    filter_job_applications_by_title
)
from fastapi.middleware.cors import CORSMiddleware

router = APIRouter(prefix="", tags=["Job Applications"])

@router.post("/", response_model=JobApplicationResponse, status_code=201)
async def create_new_job_application(
    full_name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    address: Optional[str] = Form(None),
    job_position_id: str = Form(...),
    job_position_title: str = Form(...),
    experience: Optional[str] = Form(None),
    skills: Optional[str] = Form(None),
    cover_letter: Optional[str] = Form(None),
    resume: Optional[UploadFile] = File(None),
):
    """Create a new job application with an optional resume."""
    application_data = {
        "full_name": full_name,
        "email": email,
        "phone": phone,
        "address": address,
        "job_position_id": job_position_id,
        "job_position_title": job_position_title,
        "experience": experience,
        "skills": skills,
        "cover_letter": cover_letter
    }
    return await create_job_application(JobApplicationCreate(**application_data), resume)

@router.get("/", response_model=List[JobApplicationResponse])
async def list_all_job_applications():
    """Retrieve all job applications."""
    return await get_all_job_applications()

@router.get("/filter", response_model=List[JobApplicationResponse])
async def filter_applications_by_title(job_title: str):
    """Filter job applications by job title."""
    return await filter_job_applications_by_title(job_title)

@router.get("/{application_id}", response_model=JobApplicationResponse)
async def get_single_job_application(application_id: str):
    """Retrieve a job application by ID."""
    application = await get_job_application_by_id(application_id)
    if not application:
        raise HTTPException(status_code=404, detail="Job application not found")
    return application

@router.put("/{application_id}/status", response_model=JobApplicationResponse)
async def update_application_status(application_id: str, status_update: StatusUpdate):
    """Update the status of a job application."""
    if status_update.status not in ALLOWED_STATUSES:
        raise HTTPException(
            status_code=400, 
            detail=f"Invalid status. Allowed statuses: {ALLOWED_STATUSES}"
        )
    updated_application = await update_job_application_status(application_id, status_update.status)
    if not updated_application:
        raise HTTPException(status_code=404, detail="Job application not found")
    return updated_application

@router.delete("/{application_id}")
async def remove_job_application(application_id: str):
    """Delete a job application."""
    if not await delete_job_application(application_id):
        raise HTTPException(status_code=404, detail="Job application not found")
    return {"message": "Job application deleted successfully"}