from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class ImageCreate(BaseModel):
    """Schema for creating an image."""
    name: str
    description: Optional[str] = None
    category_id: str
    file_path: str

class ImageUpdate(BaseModel):
    """Schema for updating an image."""
    name: Optional[str] = None
    description: Optional[str] = None
    category_id: Optional[str] = None
    file_path: Optional[str] = None

class ImageResponse(BaseModel):
    """Schema for responding with an image."""
    id: str
    name: str
    description: Optional[str] = None
    category_id: str
    file_path: str
    created_at: datetime

    class Config:
        from_attributes = True  # Updated from orm_mode