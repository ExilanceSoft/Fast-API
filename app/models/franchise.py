from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class FranchiseRequestCreate(BaseModel):
    user_name: str = Field(..., example="John Doe")
    user_email: EmailStr = Field(..., example="johndoe@example.com")
    user_phone: str = Field(..., example="+1234567890")
    requested_city: str = Field(..., example="New York")
    requested_state: Optional[str] = Field(None, example="NY")
    requested_country: str = Field(..., example="USA")
    investment_budget: float = Field(..., example=50000.00)
    experience_in_food_business: Optional[str] = Field(None, example="5 years managing a restaurant")
    additional_details: Optional[str] = Field(None, example="Looking for a prime location in downtown")
    request_status: str = Field(default="pending", example="pending")

class FranchiseRequestResponse(FranchiseRequestCreate):
    id: str  # MongoDB uses ObjectId, which will be stored as a string
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True