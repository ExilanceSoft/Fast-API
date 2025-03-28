from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from app.core.database import dynamodb
from app.schemas.job_position import JobPositionCreate, JobPositionResponse
from app.services.job_position_service import (
    create_job_position,
    get_all_job_positions,
    get_job_position_by_id,
    update_job_position,
    delete_job_position,
    save_image,
)

router = APIRouter()

@router.post("/", response_model=JobPositionResponse)
async def add_job_position(
    title: str = Form(...),
    description: str = Form(...),
    min_salary: float = Form(...),
    max_salary: float = Form(...),
    branch_name: str = Form(...),
    job_type: str = Form(...),
    status: str = Form(default="active"),
    image: UploadFile = File(None),
):
    """API to create a job position."""
    job_data = {
        "title": title,
        "description": description,
        "min_salary": min_salary,
        "max_salary": max_salary,
        "branch_name": branch_name,
        "job_type": job_type,
        "status": status,
        "image_url": None,
    }
    if image:
        job_data["image_url"] = await save_image(image)
    return await create_job_position(job_data)

@router.get("/", response_model=list[JobPositionResponse])
async def list_job_positions():
    """API to get all job positions."""
    return await get_all_job_positions()

@router.get("/{job_id}", response_model=JobPositionResponse)
async def retrieve_job_position(job_id: str):
    """API to get a job position by ID."""
    job = await get_job_position_by_id(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job position not found")
    return job

@router.put("/{job_id}", response_model=JobPositionResponse)
async def modify_job_position(
    job_id: str,
    title: str = Form(...),
    description: str = Form(...),
    min_salary: float = Form(...),
    max_salary: float = Form(...),
    branch_name: str = Form(...),
    job_type: str = Form(...),
    status: str = Form(default="active"),
    image: UploadFile = File(None),
):
    """API to update a job position with an optional image."""
    job_data = {
        "title": title,
        "description": description,
        "min_salary": min_salary,
        "max_salary": max_salary,
        "branch_name": branch_name,
        "job_type": job_type,
        "status": status,
    }
    if image:
        job_data["image_url"] = await save_image(image)
    return await update_job_position(job_id, job_data, image)

@router.delete("/{job_id}")
async def remove_job_position(job_id: str):
    """API to delete a job position."""
    return await delete_job_position(job_id)
