# banjos_restaurant\app\schemas\career.py
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class JobApplicationCreate(BaseModel):
    branch_id: str
    job_title: str
    applicant_name: str
    applicant_email: EmailStr
    applicant_phone: str
    resume_url: str
    cover_letter: Optional[str] = None

class JobApplicationResponse(BaseModel):
    id: str
    branch_id: str
    job_title: str
    applicant_name: str
    applicant_email: EmailStr
    applicant_phone: str
    resume_url: str
    cover_letter: Optional[str] = None
    application_status: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True