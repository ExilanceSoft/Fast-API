from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from bson import ObjectId

class TestimonialCreate(BaseModel):
    name: str
    email: EmailStr
    description: str
    rating: int
    image: Optional[str] = None

class TestimonialResponse(BaseModel):
    id: str
    name: str
    email: EmailStr
    description: str
    rating: int
    image: Optional[str] = None
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
        json_encoders = {ObjectId: str}