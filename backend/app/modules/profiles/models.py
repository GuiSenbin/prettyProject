"""个人档案模型：定义用户护肤档案表。"""
import datetime
from sqlalchemy import Boolean, Column, Date, DateTime, ForeignKey, Integer, JSON, String, Text
from sqlalchemy.orm import relationship
from backend.app.core.database import Base


class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    gender = Column(String(12), nullable=True)
    age = Column(Integer, nullable=True)
    skin_type = Column(String(32), nullable=True)
    skin_tone = Column(String(32), nullable=True)
    face_shape = Column(String(32), nullable=True)
    skin_concerns = Column(JSON, nullable=False, default=list)
    known_allergies = Column(Text, nullable=True)
    period_acne = Column(Boolean, nullable=True)
    last_period_start = Column(Date, nullable=True)
    cycle_length_days = Column(Integer, nullable=True)
    pregnancy_status = Column(String(32), nullable=True)
    preference_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)

    user = relationship("User")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "gender": self.gender,
            "age": self.age,
            "skin_type": self.skin_type,
            "skin_tone": self.skin_tone,
            "face_shape": self.face_shape,
            "skin_concerns": self.skin_concerns or [],
            "known_allergies": self.known_allergies,
            "period_acne": self.period_acne,
            "last_period_start": self.last_period_start.isoformat() if self.last_period_start else None,
            "cycle_length_days": self.cycle_length_days,
            "pregnancy_status": self.pregnancy_status,
            "preference_notes": self.preference_notes,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }
