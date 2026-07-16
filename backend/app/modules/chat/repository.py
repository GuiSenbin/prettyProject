"""AI 问答仓储：封装会话、消息和问答日志数据库访问。"""
import datetime
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload
from backend.app.modules.chat.models import ChatMessage, ChatQuestionLog, ChatSession


class ChatRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_sessions(self, user_id: str, limit: int = 10) -> list[ChatSession]:
        return self.db.execute(
            select(ChatSession)
            .where(ChatSession.user_id == user_id, ChatSession.deleted_at.is_(None))
            .order_by(ChatSession.updated_at.desc(), ChatSession.id.desc())
            .limit(limit)
        ).scalars().all()

    def get_session(self, user_id: str, session_id: int) -> ChatSession | None:
        return self.db.execute(
            select(ChatSession)
            .options(selectinload(ChatSession.messages))
            .where(
                ChatSession.id == session_id,
                ChatSession.user_id == user_id,
                ChatSession.deleted_at.is_(None),
            )
        ).scalar_one_or_none()

    def create_session(self, user_id: str, title: str) -> ChatSession:
        session = ChatSession(user_id=user_id, title=title)
        self.db.add(session)
        self.db.flush()
        return session

    def update_session_title(self, session: ChatSession, title: str, edited: bool = True) -> ChatSession:
        session.title = title
        session.title_edited = edited
        session.updated_at = datetime.datetime.now()
        self.db.commit()
        self.db.refresh(session)
        return session

    def touch_session(self, session: ChatSession) -> None:
        session.updated_at = datetime.datetime.now()

    def soft_delete_session(self, session: ChatSession) -> None:
        session.deleted_at = datetime.datetime.now()
        session.updated_at = datetime.datetime.now()
        self.db.commit()

    def add_message(
        self,
        session: ChatSession,
        role: str,
        content_text: str,
        structured_payload: dict | None = None,
        intent: str | None = None,
        subject_type: str | None = None,
    ) -> ChatMessage:
        message = ChatMessage(
            session_id=session.id,
            role=role,
            content_text=content_text,
            structured_payload=structured_payload,
            intent=intent,
            subject_type=subject_type,
        )
        self.db.add(message)
        self.touch_session(session)
        self.db.flush()
        return message

    def add_question_log(self, payload: dict) -> ChatQuestionLog:
        log = ChatQuestionLog(**payload)
        self.db.add(log)
        self.db.flush()
        return log

    def commit(self) -> None:
        self.db.commit()
