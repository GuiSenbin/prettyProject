"""用户模块 Schema：定义纯净版最小用户入参和出参。"""
from pydantic import BaseModel


class UserCreate(BaseModel):
    phone: str = ""
    display_name: str = "智颜用户"
    login_type: str = "phone"


class UserResponse(BaseModel):
    id: int
    phone: str
    display_name: str
    login_type: str
    created_at: str | None = None
    updated_at: str | None = None

    model_config = {"from_attributes": True}
