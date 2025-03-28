from pydantic import BaseModel
from datetime import datetime

class GalleryModel(BaseModel):
    """Base model for gallery categories."""
    name: str
    image_url: str
    created_at: datetime = datetime.utcnow()