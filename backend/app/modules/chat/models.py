"""AI 问答模型：定义会话、消息和脱敏日志表。"""
import datetime
from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import relationship
from backend.app.core.database import Base


class ChatSession(Base):
    __tablename__ = "chat_sessions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(80), nullable=False, default="新对话")
    title_edited = Column(Boolean, nullable=False, default=False)
    deleted_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    messages = relationship(
        "ChatMessage",
        back_populates="session",
        cascade="all, delete-orphan",
        order_by="ChatMessage.created_at",
    )


class ChatMessage(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id", ondelete="CASCADE"), nullable=False, index=True)
    role = Column(String(20), nullable=False)
    content_text = Column(Text, nullable=False)
    structured_payload = Column(JSON, nullable=True)
    intent = Column(String(40), nullable=True)
    subject_type = Column(String(40), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.now)

    session = relationship("ChatSession", back_populates="messages")


class ChatQuestionLog(Base):
    __tablename__ = "chat_question_logs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id", ondelete="SET NULL"), nullable=True)
    raw_question = Column(Text, nullable=False)
    normalized_question = Column(Text, nullable=False)
    intent = Column(String(40), nullable=True)
    subject_type = Column(String(40), nullable=True)
    context_used = Column(JSON, nullable=False, default=dict)
    answer_title = Column(String(120), nullable=True)
    source = Column(String(40), nullable=False, default="local_rule")
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.now)
