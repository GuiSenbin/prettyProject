"""个人档案服务：处理档案归属校验和条件字段清理。"""
from fastapi import HTTPException
from sqlalchemy.orm import Session
from backend.app.modules.profiles.models import UserProfile
from backend.app.modules.profiles.repository import ProfileRepository
from backend.app.modules.profiles.schemas import ProfilePayload
from backend.app.modules.users.repository import UserRepository


class ProfileService:
    def __init__(self, db: Session):
        self.profiles = ProfileRepository(db)
        self.users = UserRepository(db)

    def get(self, user_id: str) -> UserProfile | None:
        self._ensure_user_exists(user_id)
        return self.profiles.get_by_user_id(user_id)

    def save(self, user_id: str, payload: ProfilePayload) -> UserProfile:
        self._ensure_user_exists(user_id)
        data = self._normalize(payload)
        return self.profiles.upsert(user_id, data)

    def _ensure_user_exists(self, user_id: str) -> None:
        if not self.users.get(user_id):
            raise HTTPException(404, "用户不存在")

    def _normalize(self, payload: ProfilePayload) -> dict:
        data = payload.model_dump()
        if data["gender"] != "female":
            data["period_acne"] = None
            data["last_period_start"] = None
            data["cycle_length_days"] = None
            data["pregnancy_status"] = None
        elif not data["age"] or data["age"] < 18 or data["age"] > 50:
            data["pregnancy_status"] = None
        data["skin_concerns"] = data.get("skin_concerns") or []
        return data
