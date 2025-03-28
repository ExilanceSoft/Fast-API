from pydantic import BaseModel, EmailStr, field_validator, ConfigDict
from typing import Optional, Literal
from datetime import datetime
from enum import Enum

class ApplicationStatus(str, Enum):
    PENDING = "Pending"
    UNDER_REVIEW = "Under Review"
    INTERVIEW_SCHEDULED = "Interview Scheduled"
    INTERVIEWED = "Interviewed"
    SELECTED = "Selected"
    REJECTED = "Rejected"
    ON_HOLD = "On Hold"
    WITHDRAWN = "Withdrawn"

ALLOWED_STATUSES = [status.value for status in ApplicationStatus]

class JobApplicationBase(BaseModel):
    full_name: str
    email: EmailStr
    phone: str
    address: Optional[str] = None
    job_position_id: str
    job_position_title: str
    experience: Optional[str] = None
    skills: Optional[str] = None
    cover_letter: Optional[str] = None
    resume_url: Optional[str] = None
    status: str = ApplicationStatus.PENDING.value

    @field_validator('status')
    def validate_status(cls, v):
        if v.lower() in [s.lower() for s in ALLOWED_STATUSES]:
            for status in ALLOWED_STATUSES:
                if v.lower() == status.lower():
                    return status
        raise ValueError(f"Invalid status. Allowed statuses: {ALLOWED_STATUSES}")

class JobApplicationCreate(JobApplicationBase):
    pass

class StatusUpdate(BaseModel):
    status: str

    @field_validator('status')
    def validate_status(cls, v):
        if v.lower() in [s.lower() for s in ALLOWED_STATUSES]:
            for status in ALLOWED_STATUSES:
                if v.lower() == status.lower():
                    return status
        raise ValueError(f"Invalid status. Allowed statuses: {ALLOWED_STATUSES}")

class JobApplicationResponse(JobApplicationBase):
    id: str
    created_at: str  # Changed from datetime to str
    updated_at: str  # Changed from datetime to str

    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat() if hasattr(v, 'isoformat') else str(v)
        }
    )