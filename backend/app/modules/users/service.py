"""用户模块服务：处理用户档案业务规则。"""
from fastapi import HTTPException
from sqlalchemy.orm import Session
from backend.app.core.security import get_password_hash, verify_password
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

    def register_user(self, username: str, password: str, display_name: str = "智颜用户") -> User:
        """用户注册：用户名查重后加盐散列密码并写入双表"""
        existing_auth = self.users.get_auth("username", username)
        if existing_auth:
            raise HTTPException(400, "该用户名已被注册")

        # 1. 新建核心 User 账号主体
        user = self.users.create({
            "display_name": display_name,
            "login_type": "username"
        })

        # 2. 生成安全密码散列值，并写入 user_social_auths 授权映射表中
        password_hash = get_password_hash(password)
        self.users.create_auth(
            user_id=user.id,
            identity_type="username",
            identifier=username,
            credential=password_hash
        )
        return user

    def authenticate_user(self, username: str, password: str) -> User:
        """用户登录：支持用户名或绑定手机号匹配，通过慢哈希核对安全密码"""
        # 1. 尝试匹配 username 认证
        auth = self.users.get_auth("username", username)
        if not auth:
            # 2. 尝试匹配 phone 手机号认证
            auth = self.users.get_auth("phone", username)

        if not auth:
            raise HTTPException(401, "账号不存在或密码错误")

        # 3. 比对加盐哈希值
        if not verify_password(password, auth.credential):
            raise HTTPException(401, "账号不存在或密码错误")

        return auth.user

