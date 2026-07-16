"""AI 问答路由：提供多会话历史、消息发送、重命名和删除接口。"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.core.deps import get_current_user_id, get_db
from backend.app.core.schemas import StandardResponse
from backend.app.modules.chat.schemas import (
    ChatMessageCreate,
    ChatSendResponse,
    ChatSessionDetail,
    ChatSessionSummary,
    ChatSessionUpdate,
)
from backend.app.modules.chat.service import ChatService

router = APIRouter(prefix="/chat", tags=["AI问答"])


@router.get("/sessions", response_model=StandardResponse[list[ChatSessionSummary]])
def list_chat_sessions(user_id: str = Depends(get_current_user_id), db: Session = Depends(get_db)):
    items = ChatService(db).list_sessions(user_id)
    return {"code": 200, "message": "success", "data": items}


@router.get("/sessions/{session_id}", response_model=StandardResponse[ChatSessionDetail])
def get_chat_session(session_id: int, user_id: str = Depends(get_current_user_id), db: Session = Depends(get_db)):
    detail = ChatService(db).get_session_detail(user_id, session_id)
    return {"code": 200, "message": "success", "data": detail}


@router.patch("/sessions/{session_id}", response_model=StandardResponse[ChatSessionSummary])
def rename_chat_session(
    session_id: int,
    payload: ChatSessionUpdate,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    item = ChatService(db).rename_session(user_id, session_id, payload.title)
    return {"code": 200, "message": "success", "data": item}


@router.delete("/sessions/{session_id}", response_model=StandardResponse[dict])
def delete_chat_session(session_id: int, user_id: str = Depends(get_current_user_id), db: Session = Depends(get_db)):
    result = ChatService(db).delete_session(user_id, session_id)
    return {"code": 200, "message": "success", "data": result}


@router.post("/messages", response_model=StandardResponse[ChatSendResponse])
def send_chat_message(
    payload: ChatMessageCreate,
    user_id: str = Depends(get_current_user_id),
    db: Session = Depends(get_db),
):
    result = ChatService(db).send_message(user_id, payload)
    return {"code": 200, "message": "success", "data": result}
