from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class MenuCreate(BaseModel):
    name: str
    description: str
    category_name: str
    price: float
    parcel_price: Optional[float] = None
    is_available: bool = True
    is_veg: bool = True

class MenuUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    category_name: Optional[str] = None
    price: Optional[float] = None
    parcel_price: Optional[float] = None
    is_available: Optional[bool] = None
    is_veg: Optional[bool] = None

class MenuResponse(BaseModel):
    id: str
    name: str
    description: str
    category_name: str
    price: float
    parcel_price: Optional[float] = None
    image_url: Optional[str] = None
    is_available: bool
    is_veg: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True