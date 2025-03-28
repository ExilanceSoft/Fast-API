from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from typing import Optional, List
from app.schemas.menu import MenuCreate, MenuUpdate, MenuResponse
from app.services.menu_service import (
    create_menu_item,
    get_menu_item,
    get_all_menu_items,
    get_menu_items_by_category,
    update_menu_item,
    delete_menu_item,
)

router = APIRouter(prefix="", tags=["Menu"])

@router.post("/add", response_model=MenuResponse)
async def add_menu_item(
    name: str = Form(...),
    description: str = Form(...),
    category_name: str = Form(...),
    price: float = Form(...),
    parcel_price: Optional[float] = Form(None),
    is_available: bool = Form(True),
    is_veg: bool = Form(True),
    image: Optional[UploadFile] = File(None),
):
    """Add a new menu item."""
    menu_data = {
        "name": name,
        "description": description,
        "category_name": category_name,
        "price": price,
        "parcel_price": parcel_price,
        "is_available": is_available,
        "is_veg": is_veg,
    }
    return await create_menu_item(menu_data, image)

@router.get("", response_model=List[MenuResponse])
async def list_menu_items():
    """Retrieve all menu items."""
    return await get_all_menu_items()

@router.get("/category/{category_name}", response_model=List[MenuResponse])
async def get_menu_items_by_category_route(category_name: str):
    """Retrieve menu items by category name."""
    items = await get_menu_items_by_category(category_name)  # This should call the service method
    if not items:
        raise HTTPException(status_code=404, detail="No menu items found for this category")
    return items


@router.get("/{menu_id}", response_model=MenuResponse)
async def get_menu_item_by_id(menu_id: str):
    """Retrieve a menu item by its ID."""
    item = await get_menu_item(menu_id)
    if not item:
        raise HTTPException(status_code=404, detail="Menu item not found")
    return item

@router.put("/{menu_id}", response_model=MenuResponse)
async def update_menu_item_by_id(
    menu_id: str,
    name: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    category_name: Optional[str] = Form(None),
    price: Optional[float] = Form(None),
    parcel_price: Optional[float] = Form(None),
    is_available: Optional[bool] = Form(None),
    is_veg: Optional[bool] = Form(None),
    image: Optional[UploadFile] = File(None),
):
    """Update a menu item by its ID."""
    menu_data = {
        "name": name,
        "description": description,
        "category_name": category_name,
        "price": price,
        "parcel_price": parcel_price,
        "is_available": is_available,
        "is_veg": is_veg,
    }
    updated_item = await update_menu_item(menu_id, menu_data, image)
    if not updated_item:
        raise HTTPException(status_code=404, detail="Menu item not found")
    return updated_item

@router.delete("/{menu_id}")
async def delete_menu_item_by_id(menu_id: str):
    """Delete a menu item by its ID."""
    if not await delete_menu_item(menu_id):
        raise HTTPException(status_code=404, detail="Menu item not found")
    return {"message": "Menu item deleted successfully"}