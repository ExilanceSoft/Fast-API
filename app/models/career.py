# banjos_restaurant\app\models\career.py
from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime

class JobApplicationModel(BaseModel):
    id: Optional[str] = None  # Make id optional
    branch_id: str
    job_title: str
    applicant_name: str
    applicant_email: EmailStr
    applicant_phone: str
    resume_url: str
    cover_letter: Optional[str] = None
    application_status: str = "pending"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True