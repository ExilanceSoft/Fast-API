# banjos_restaurant\app\schemas\user.py
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
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr = Field(...)
    mobile_number: str = Field(...)

    @validator("mobile_number")
    def validate_mobile_number(cls, v):
        if not re.match(r"^\+?[1-9]\d{1,14}$", v):
            raise ValueError("Mobile number must be in E.164 format")
        return v

class UserRegister(UserBase):
    password: str = Field(..., min_length=8, max_length=50)
    role: UserRole = Field(default=UserRole.USER)

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

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(UserBase):
    id: str
    role: UserRole
    disabled: bool = False

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    refresh_token: str
    csrf_token: str

class TokenData(BaseModel):
    username: Optional[str] = None