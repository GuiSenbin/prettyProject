"""用户资料模型"""
import datetime
from sqlalchemy import Column, Integer, String, DateTime, JSON
from backend.app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(50), nullable=False, default="用户")
    age = Column(String(20), default="")
    gender = Column(String(10), default="")
    skin_type = Column(String(20), default="")
    face_shape = Column(String(20), default="")
    skin_tone = Column(String(20), default="")
    concerns = Column(JSON, default=list)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "age": self.age,
            "gender": self.gender,
            "skin_type": self.skin_type,
            "face_shape": self.face_shape,
            "skin_tone": self.skin_tone,
            "concerns": self.concerns or [],
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
