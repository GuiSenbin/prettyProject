"""个人档案仓储：封装用户档案数据库读写。"""
from sqlalchemy import select
from sqlalchemy.orm import Session
from backend.app.modules.profiles.models import UserProfile


class ProfileRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_user_id(self, user_id: str) -> UserProfile | None:
        return self.db.execute(
            select(UserProfile).where(UserProfile.user_id == user_id)
        ).scalar_one_or_none()

    def upsert(self, user_id: str, data: dict) -> UserProfile:
        profile = self.get_by_user_id(user_id)
        if profile:
            for key, value in data.items():
                setattr(profile, key, value)
        else:
            profile = UserProfile(user_id=user_id, **data)
            self.db.add(profile)
        self.db.commit()
        self.db.refresh(profile)
        return profile
