"""AI 问答 Schema：定义会话、消息和问答接口数据结构。"""
from pydantic import BaseModel, Field


class ChatMessageCreate(BaseModel):
    message: str = Field(min_length=1, max_length=1200)
    session_id: int | None = None


class ChatSessionUpdate(BaseModel):
    title: str = Field(min_length=1, max_length=40)


class ChatSessionSummary(BaseModel):
    id: int
    title: str
    title_edited: bool = False
    updated_at: str | None = None
    created_at: str | None = None


class ChatMessageResponse(BaseModel):
    id: int
    role: str
    content_text: str
    structured_payload: dict | None = None
    intent: str | None = None
    subject_type: str | None = None
    created_at: str | None = None


class ChatSendResponse(BaseModel):
    session: ChatSessionSummary
    user_message: ChatMessageResponse
    message: ChatMessageResponse


class ChatSessionDetail(BaseModel):
    session: ChatSessionSummary
    messages: list[ChatMessageResponse] = Field(default_factory=list)
