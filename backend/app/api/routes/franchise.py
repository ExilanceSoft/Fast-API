from fastapi import APIRouter, HTTPException
from app.core.database import dynamodb
from typing import List
from app.models.franchise import FranchiseRequestCreate, FranchiseRequestResponse
from app.services.franchise_service import (
    create_franchise_request,
    get_all_requests,
    get_request_by_id,
    update_request_status,
    delete_request,
)

router = APIRouter()

@router.post("/requests/", response_model=FranchiseRequestResponse)
async def add_franchise_request(request_data: FranchiseRequestCreate):
    """API to create a franchise request"""
    return await create_franchise_request(request_data)

@router.get("/requests/", response_model=List[FranchiseRequestResponse])
async def list_franchise_requests():
    """API to get all franchise requests"""
    return await get_all_requests()

@router.get("/requests/{request_id}", response_model=FranchiseRequestResponse)
async def retrieve_franchise_request(request_id: str):
    """API to get a franchise request by ID"""
    request = await get_request_by_id(request_id)
    if not request:
        raise HTTPException(status_code=404, detail="Franchise request not found")
    return request

@router.put("/requests/{request_id}/status/{status}", response_model=FranchiseRequestResponse)
async def modify_request_status(request_id: str, status: str):
    """API to update a franchise request status"""
    updated_request = await update_request_status(request_id, status)
    if not updated_request:
        raise HTTPException(status_code=404, detail="Franchise request not found")
    return updated_request

@router.delete("/requests/{request_id}")
async def remove_request(request_id: str):
    """API to delete a franchise request"""
    if not await delete_request(request_id):
        raise HTTPException(status_code=404, detail="Franchise request not found")
    return {"message": "Franchise request deleted successfully"}