"""聊天与 AI 问答 API"""
import uuid
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import select

from backend.app.core.deps import get_db
from backend.app.models.user import User
from backend.app.models.chat import ChatMessage
from backend.app.schemas.chat import ChatRequest, ChatResponse, ChatHistoryResponse
from backend.app.services.ai_service import BeautyAIService

router = APIRouter(prefix="/chat", tags=["AI 问答"])


def _get_user_summary(user_id: int | None, db: Session) -> dict | None:
    if not user_id:
        return None
    user = db.get(User, user_id)
    if not user:
        return None
    return {
        "name": user.name,
        "age": user.age,
        "skin_type": user.skin_type,
        "face_shape": user.face_shape,
        "skin_tone": user.skin_tone,
        "concerns": user.concerns or [],
    }


@router.post("/", response_model=ChatResponse)
def chat(request: ChatRequest, db: Session = Depends(get_db)):
    """发送消息，获取 AI 实时回复"""
    message = request.message.strip()
    if not message:
        return ChatResponse(reply="请输入你的问题~ 😊", session_id=request.session_id)

    session_id = request.session_id or "default"

    # 保存用户消息
    db.add(ChatMessage(
        user_id=request.user_id, session_id=session_id,
        role="user", content=message,
    ))
    db.commit()

    # 获取最近对话历史
    history = db.execute(
        select(ChatMessage)
        .where(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.id.desc()).limit(10)
    ).scalars().all()
    history.reverse()
    history_dicts = [{"role": m.role, "content": m.content} for m in history]

    # 调用 AI
    user_summary = _get_user_summary(request.user_id, db)
    ai = BeautyAIService(db_session=db)
    reply = ai.chat(message, history_dicts, user_summary)

    # 保存 AI 回复
    db.add(ChatMessage(
        user_id=request.user_id, session_id=session_id,
        role="assistant", content=reply,
    ))
    db.commit()

    return ChatResponse(reply=reply, session_id=session_id)


@router.get("/history", response_model=list[ChatHistoryResponse])
def get_history(session_id: str = Query("default"), db: Session = Depends(get_db)):
    messages = db.execute(
        select(ChatMessage)
        .where(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.id)
    ).scalars().all()
    return [m.to_dict() for m in messages]


@router.delete("/history")
def clear_history(session_id: str = Query("default"), db: Session = Depends(get_db)):
    db.execute(
        ChatMessage.__table__.delete().where(ChatMessage.session_id == session_id)
    )
    db.commit()
    return {"ok": True}


@router.post("/new-session")
def new_session():
    return {"session_id": str(uuid.uuid4())[:8]}
