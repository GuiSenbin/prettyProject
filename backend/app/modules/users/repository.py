"""用户模块仓储：封装用户档案数据库读写。"""
from sqlalchemy import select
from sqlalchemy.orm import Session
from backend.app.modules.users.models import User


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def latest(self) -> User | None:
        return self.db.execute(select(User).order_by(User.id.desc()).limit(1)).scalar_one_or_none()

    def get(self, user_id: int) -> User | None:
        return self.db.get(User, user_id)

    def create(self, data: dict) -> User:
        user = User(**data)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def update(self, user: User, data: dict) -> User:
        for key, value in data.items():
            setattr(user, key, value)
        self.db.commit()
        self.db.refresh(user)
        return user

    def delete(self, user: User) -> None:
        self.db.delete(user)
        self.db.commit()
