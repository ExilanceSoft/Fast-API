from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime
from bson import ObjectId

class PyObjectId(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return str(v)

class Testimonial(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    name: str = Field(..., description="Name of the user submitting the testimonial")
    email: EmailStr = Field(..., description="Email of the user submitting the testimonial")
    description: str = Field(..., description="Testimonial description")
    rating: int = Field(..., ge=1, le=5, description="Rating from 1 to 5")
    image: Optional[str] = Field(None, description="URL of the testimonial image")
    status: str = Field(default="pending", description="Status of the testimonial (pending/approved/rejected)")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="Timestamp of testimonial submission")

    class Config:
        allow_population_by_field_name = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "name": "John Doe",
                "email": "john.doe@example.com",
                "description": "Great food and service!",
                "rating": 5,
                "image": "https://example.com/image.jpg",
                "status": "pending"
            }
        }