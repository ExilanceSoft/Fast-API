# banjos_restaurant\app\models\categories.py
from pydantic import BaseModel
from datetime import datetime

class CategoryModel(BaseModel):
    id: str
    name: str
    created_at: datetime = datetime.utcnow()

    class Config:
        from_attributes = True