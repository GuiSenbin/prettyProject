"""用户模块 Schema：定义企业级用户入参和出参。"""
from pydantic import BaseModel


class UserCreate(BaseModel):
    phone: str | None = None
    display_name: str = "智颜用户"
    login_type: str = "username"


class UserUpdate(BaseModel):
    phone: str | None = None
    display_name: str | None = None
    login_type: str | None = None
    avatar_url: str | None = None


class UserRegister(BaseModel):
    username: str
    password: str
    display_name: str = "智颜用户"


class UserLogin(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    id: str
    phone: str | None = None
    display_name: str
    avatar_url: str | None = None
    login_type: str
    created_at: str | None = None
    updated_at: str | None = None

    model_config = {"from_attributes": True}

