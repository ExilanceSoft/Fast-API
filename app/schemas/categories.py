# banjos_restaurant\app\schemas\categories.py
from pydantic import BaseModel
from datetime import datetime
from typing import Optional 

class CategoryCreate(BaseModel):
    name: str

class CategoryUpdate(BaseModel):
    name: Optional[str] = None

class CategoryResponse(BaseModel):
    id: str
    name: str
    created_at: datetime = datetime.utcnow()

    class Config:
        from_attributes = True