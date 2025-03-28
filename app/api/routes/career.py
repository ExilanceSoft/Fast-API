# banjos_restaurant\app\api\routes\career.py
from fastapi import APIRouter, HTTPException
from app.schemas.career import JobApplicationCreate, JobApplicationResponse
from app.services.career_service import apply_for_job, get_all_applications, get_application_by_id, update_application_status
from typing import List

router = APIRouter(prefix="/career", tags=["Career"])

@router.post("/apply", response_model=JobApplicationResponse)
async def submit_job_application(application: JobApplicationCreate):
    """Submit a job application."""
    new_application = await apply_for_job(application.dict())
    return JobApplicationResponse(**new_application.dict())

@router.get("/applications", response_model=List[JobApplicationResponse])
async def list_all_applications():
    """Retrieve all job applications."""
    return await get_all_applications()

@router.get("/applications/{application_id}", response_model=JobApplicationResponse)
async def get_application(application_id: str):
    """Retrieve a job application by its ID."""
    application = await get_application_by_id(application_id)
    if not application:
        raise HTTPException(status_code=404, detail="Job application not found")
    return application

@router.put("/applications/{application_id}/status", response_model=JobApplicationResponse)
async def update_status(application_id: str, status: str):
    """Update the status of a job application."""
    updated_application = await update_application_status(application_id, status)
    if not updated_application:
        raise HTTPException(status_code=404, detail="Job application not found")
    return updated_application