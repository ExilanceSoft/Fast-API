from pydantic import BaseModel
from typing import Optional

class OnlineOrderLinkCreate(BaseModel):
    platform: str
    url: str
    logo: str
    branch_id: str

class OnlineOrderLinkUpdate(BaseModel):
    platform: Optional[str] = None
    url: Optional[str] = None
    logo: Optional[str] = None
    branch_id: Optional[str] = None
