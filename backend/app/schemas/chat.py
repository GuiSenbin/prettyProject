"""聊天 Schema"""
from pydantic import BaseModel


class ChatRequest(BaseModel):
    message: str
    user_id: int | None = None
    session_id: str = "default"
    user_products: list[str] | None = None


class ChatResponse(BaseModel):
    reply: str
    session_id: str


class ChatHistoryResponse(BaseModel):
    id: int
    role: str
    content: str
    created_at: str | None = None

    model_config = {"from_attributes": True}
