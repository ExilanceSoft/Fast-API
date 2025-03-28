from pydantic import BaseModel
from datetime import datetime

class ImageModel(BaseModel):
    """Base model for images."""
    name: str
    description: Optional[str] = None
    category_id: str
    file_path: str
    created_at: datetime = datetime.utcnow()