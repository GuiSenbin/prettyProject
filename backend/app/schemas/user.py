"""用户 Schema"""
from pydantic import BaseModel


class UserCreate(BaseModel):
    name: str = "用户"
    age: str = ""
    gender: str = ""
    skin_type: str = ""
    face_shape: str = ""
    skin_tone: str = ""
    concerns: list[str] = []


class UserResponse(BaseModel):
    id: int
    name: str
    age: str
    gender: str
    skin_type: str
    face_shape: str
    skin_tone: str
    concerns: list[str]
    created_at: str | None = None
    updated_at: str | None = None

    model_config = {"from_attributes": True}
