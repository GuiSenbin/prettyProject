"""用户模块模型：定义纯净版最小用户表。"""
import datetime
from sqlalchemy import Column, DateTime, Integer, String
from backend.app.core.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    phone = Column(String(32), nullable=False, default="")
    display_name = Column(String(50), nullable=False, default="智颜用户")
    login_type = Column(String(20), nullable=False, default="phone")
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "phone": self.phone,
            "display_name": self.display_name,
            "login_type": self.login_type,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
