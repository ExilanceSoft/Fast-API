from pydantic import BaseModel, Field
from typing import Optional
from bson import ObjectId

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

class OnlineOrderLinkModel(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id")
    platform: str
    url: str
    logo: str
    branch_id: str

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
