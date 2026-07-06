"""用户模块仓储：封装用户档案数据库读写。"""
from sqlalchemy import select
from sqlalchemy.orm import Session
from backend.app.modules.users.models import User, UserAuth


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

    def get_auth(self, identity_type: str, identifier: str) -> UserAuth | None:
        """根据认证渠道与渠道标识查询授权凭证"""
        return self.db.execute(
            select(UserAuth).where(
                UserAuth.identity_type == identity_type,
                UserAuth.identifier == identifier
            )
        ).scalar_one_or_none()

    def create_auth(self, user_id: int, identity_type: str, identifier: str, credential: str | None = None) -> UserAuth:
        """新建一条关联的登录凭证映射"""
        auth = UserAuth(user_id=user_id, identity_type=identity_type, identifier=identifier, credential=credential)
        self.db.add(auth)
        self.db.commit()
        self.db.refresh(auth)
        return auth

