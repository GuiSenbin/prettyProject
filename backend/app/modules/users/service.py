"""用户模块服务：处理用户档案业务规则。"""
from fastapi import HTTPException
from sqlalchemy.orm import Session
from backend.app.modules.users.models import User
from backend.app.modules.users.repository import UserRepository


class UserService:
    def __init__(self, db: Session):
        self.users = UserRepository(db)

    def latest(self) -> User | None:
        return self.users.latest()

    def create(self, payload: dict) -> User:
        return self.users.create(payload)

    def update(self, user_id: int, payload: dict) -> User:
        user = self.get_or_404(user_id)
        return self.users.update(user, payload)

    def get_or_404(self, user_id: int) -> User:
        user = self.users.get(user_id)
        if not user:
            raise HTTPException(404, "用户不存在")
        return user

    def delete(self, user_id: int) -> None:
        user = self.get_or_404(user_id)
        self.users.delete(user)
