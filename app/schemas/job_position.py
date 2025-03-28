# banjos_restaurant\app\schemas\job_position.py
from pydantic import BaseModel, Field, validator
from datetime import datetime
from typing import Optional

class JobPositionBase(BaseModel):
    title: str
    description: str
    min_salary: float
    max_salary: float
    branch_name: str
    job_type: str
    status: str = Field(default="active", pattern="^(active|inactive)$")
    image_url: Optional[str] = None

    @validator("min_salary", "max_salary")
    def validate_salary(cls, value):
        if value < 0:
            raise ValueError("Salary must be a positive number")
        return value

    @validator("branch_name")
    def validate_branch_name(cls, value):
        if not value.strip():
            raise ValueError("Branch name cannot be empty")
        return value

class JobPositionCreate(JobPositionBase):
    pass

class JobPositionResponse(JobPositionBase):
    id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }