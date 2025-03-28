from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Literal
from datetime import datetime

ALLOWED_STATUSES = (
    "Pending",
    "Under Review",
    "Interview Scheduled",
    "Interviewed",
    "Selected",
    "Rejected",
    "On Hold",
    "Withdrawn"
)

class JobApplicationBase(BaseModel):
    id: str
    full_name: str
    email: EmailStr
    phone: str
    address: Optional[str] = None
    job_position_id: str
    job_position_title: Optional[str] = None  # Include job title for filtering
    experience: Optional[str] = None
    skills: Optional[str] = None
    cover_letter: Optional[str] = None
    resume_url: Optional[str] = None
    status: Literal[
        "Pending", 
        "Under Review", 
        "Interview Scheduled", 
        "Interviewed", 
        "Selected", 
        "Rejected", 
        "On Hold", 
        "Withdrawn"
    ] = "Pending"

class JobApplicationCreate(JobApplicationBase):
    pass

class JobApplicationResponse(JobApplicationBase):
    created_at: datetime
    updated_at: datetime

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }