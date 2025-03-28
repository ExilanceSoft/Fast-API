# banjos_restaurant\app\models\user.py
from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from enum import Enum
import re

class UserRole(str, Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    SUPERADMIN = "superadmin"
    USER = "user"

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=50, description="Username must be between 3 and 50 characters")
    email: EmailStr = Field(..., description="A valid email address is required")
    mobile_number: str = Field(..., description="A valid mobile number is required")

    @validator("mobile_number")
    def validate_mobile_number(cls, v):
        if not re.match(r"^\+?[1-9]\d{1,14}$", v):
            raise ValueError("Mobile number must be in E.164 format")
        return v

class UserCreate(UserBase):
    password: str = Field(..., min_length=8, max_length=50, description="Password must be between 8 and 50 characters")
    role: UserRole = Field(default=UserRole.USER, description="User role")

    @validator("password")
    def validate_password(cls, v):
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"[0-9]", v):
            raise ValueError("Password must contain at least one digit")
        if not re.search(r"[!@#$%^&*()_+]", v):
            raise ValueError("Password must contain at least one special character")
        return v

class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = Field(None)
    mobile_number: Optional[str] = Field(None)
    password: Optional[str] = Field(None, min_length=8, max_length=50)

class UserModel(UserBase):
    id: str
    role: UserRole
    disabled: bool = False

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": "123e4567-e89b-12d3-a456-426614174000",
                "username": "johndoe",
                "email": "johndoe@example.com",
                "mobile_number": "+1234567890",
                "role": "user",
                "disabled": False
            }
        }

class Token(BaseModel):
    access_token: str
    token_type: str
    refresh_token: str
    csrf_token: str

class TokenData(BaseModel):
    username: Optional[str] = None