from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class MenuModel(BaseModel):
    id: str = Field(..., alias="_id")  # Convert MongoDB _id to id
    name: str
    description: str
    category_name: str
    price: float
    parcel_price: Optional[float] = None
    image_url: Optional[str] = None  # URL to the uploaded image
    is_available: bool = True
    is_veg: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        populate_by_name = True  # Ensures alias `_id` is respected
        from_attributes = True