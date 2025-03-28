# banjos_restaurant\app\api\routes\branches.py
from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from app.schemas.branches import BranchCreate, BranchResponse
from app.services.branches_service import create_branch, get_branch, update_branch, delete_branch, get_all_branches
from typing import List, Optional

router = APIRouter(prefix="", tags=["Branches"])

@router.post("/", response_model=BranchResponse)
async def create_new_branch(
    name: str = Form(...),
    latitude: float = Form(...),
    longitude: float = Form(...),
    address: str = Form(...),
    city: str = Form(...),
    state: Optional[str] = Form(None),
    country: str = Form(...),
    zipcode: Optional[str] = Form(None),
    phone_number: Optional[str] = Form(None),
    email: Optional[str] = Form(None),
    opening_hours: Optional[str] = Form(None),
    manager_name: Optional[str] = Form(None),
    branch_opening_date: Optional[str] = Form(None),
    branch_status: str = Form("open"),
    seating_capacity: Optional[int] = Form(None),
    parking_availability: bool = Form(False),
    wifi_availability: bool = Form(False),
    image: Optional[UploadFile] = File(None),
):
    """Create a new branch with an optional image."""
    branch_data = {
        "name": name,
        "latitude": latitude,
        "longitude": longitude,
        "address": address,
        "city": city,
        "state": state,
        "country": country,
        "zipcode": zipcode,
        "phone_number": phone_number,
        "email": email,
        "opening_hours": opening_hours,
        "manager_name": manager_name,
        "branch_opening_date": branch_opening_date,
        "branch_status": branch_status,
        "seating_capacity": seating_capacity,
        "parking_availability": parking_availability,
        "wifi_availability": wifi_availability,
    }
    
    new_branch = await create_branch(branch_data, image)
    return BranchResponse(**new_branch.dict())

@router.get("/", response_model=List[BranchResponse])
async def list_branches():
    """Retrieve all branches."""
    return await get_all_branches()

@router.get("/{branch_id}", response_model=BranchResponse)
async def get_branch_by_id(branch_id: str):
    """Retrieve a branch by its ID."""
    branch = await get_branch(branch_id)
    if not branch:
        raise HTTPException(status_code=404, detail="Branch not found")
    return branch

@router.put("/{branch_id}", response_model=BranchResponse)
async def update_branch_by_id(
    branch_id: str,
    name: str = Form(...),
    latitude: float = Form(...),
    longitude: float = Form(...),
    address: str = Form(...),
    city: str = Form(...),
    state: Optional[str] = Form(None),
    country: str = Form(...),
    zipcode: Optional[str] = Form(None),
    phone_number: Optional[str] = Form(None),
    email: Optional[str] = Form(None),
    opening_hours: Optional[str] = Form(None),
    manager_name: Optional[str] = Form(None),
    branch_opening_date: Optional[str] = Form(None),
    branch_status: str = Form("open"),
    seating_capacity: Optional[int] = Form(None),
    parking_availability: bool = Form(False),
    wifi_availability: bool = Form(False),
    image: Optional[UploadFile] = File(None),
):
    """Update a branch with an optional image."""
    branch_data = {
        "name": name,
        "latitude": latitude,
        "longitude": longitude,
        "address": address,
        "city": city,
        "state": state,
        "country": country,
        "zipcode": zipcode,
        "phone_number": phone_number,
        "email": email,
        "opening_hours": opening_hours,
        "manager_name": manager_name,
        "branch_opening_date": branch_opening_date,
        "branch_status": branch_status,
        "seating_capacity": seating_capacity,
        "parking_availability": parking_availability,
        "wifi_availability": wifi_availability,
    }
    
    updated_branch = await update_branch(branch_id, branch_data, image)
    if not updated_branch:
        raise HTTPException(status_code=404, detail="Branch not found")
    return updated_branch

@router.delete("/{branch_id}")
async def delete_branch_by_id(branch_id: str):
    """Delete a branch."""
    if not await delete_branch(branch_id):
        raise HTTPException(status_code=404, detail="Branch not found")
    return {"message": "Branch deleted successfully"}