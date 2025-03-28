from fastapi import APIRouter, HTTPException, UploadFile, File, Form
from app.services.online_order_link_service import OnlineOrderLinkService
from app.schemas.online_order_link import OnlineOrderLinkCreate, OnlineOrderLinkUpdate
import os
import shutil
from uuid import uuid4

router = APIRouter()

# Directory to store uploaded images
IMAGE_DIR = "static/images"
os.makedirs(IMAGE_DIR, exist_ok=True)

@router.get("/")
async def get_links():
    return await OnlineOrderLinkService.get_all_links()

@router.post("/")
async def create_link(
    platform: str = Form(...),
    url: str = Form(...),
    branch_id: str = Form(...),
    logo: UploadFile = File(...)
):
    logo_filename = f"{uuid4()}_{logo.filename}"
    logo_path = os.path.join(IMAGE_DIR, logo_filename)
    with open(logo_path, "wb") as buffer:
        shutil.copyfileobj(logo.file, buffer)

    # Store the relative path to the logo
    link_data = OnlineOrderLinkCreate(
        platform=platform,
        url=url,
        logo=f"/static/images/{logo_filename}",
        branch_id=branch_id
    )
    link_id = await OnlineOrderLinkService.create_link(link_data)
    return {"message": "Link created successfully", "id": link_id}

@router.get("/{link_id}")
async def get_link(link_id: str):
    link = await OnlineOrderLinkService.get_link_by_id(link_id)
    if not link:
        raise HTTPException(status_code=404, detail="Link not found")
    return link

@router.put("/{link_id}")
async def update_link(
    link_id: str,
    platform: str = Form(...),
    url: str = Form(...),
    branch_id: str = Form(...),
    logo: UploadFile = File(None)
):
    update_data = {}
    if logo:
        logo_filename = f"{uuid4()}_{logo.filename}"
        logo_path = os.path.join(IMAGE_DIR, logo_filename)
        with open(logo_path, "wb") as buffer:
            shutil.copyfileobj(logo.file, buffer)
        update_data['logo'] = f"/static/images/{logo_filename}"

    update_data['platform'] = platform
    update_data['url'] = url
    update_data['branch_id'] = branch_id

    await OnlineOrderLinkService.update_link(link_id, OnlineOrderLinkUpdate(**update_data))
    return {"message": "Link updated successfully"}

@router.delete("/{link_id}")
async def delete_link(link_id: str):
    await OnlineOrderLinkService.delete_link(link_id)
    return {"message": "Link deleted successfully"}