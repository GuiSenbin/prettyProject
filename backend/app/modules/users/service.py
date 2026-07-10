"""用户模块服务：处理用户档案业务规则。"""
import re
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

    def update(self, user_id: str, payload: dict) -> User:
        user = self.get_or_404(user_id)
        
        # 处理凭证同步更新
        new_username = payload.get("display_name")
        new_phone = payload.get("phone")
        
        if new_username and new_username != user.display_name:
            # 查重
            existing_username = self.users.get_auth("username", new_username)
            if existing_username and str(existing_username.user_id) != str(user.id):
                raise HTTPException(400, "该用户名已被占用")
            # 更新或创建 auth 记录
            auths = self.users.get_auths_by_user(user_id)
            username_auth = next((a for a in auths if a.identity_type == "username"), None)
            if username_auth:
                self.users.update_auth_identifier(username_auth, new_username)
            else:
                # 寻找现有密码复用
                credential = auths[0].credential if auths else None
                self.users.create_auth(user_id, "username", new_username, credential)
                
        if new_phone and new_phone != user.phone:
            existing_phone = self.users.get_auth("phone", new_phone)
            if existing_phone and str(existing_phone.user_id) != str(user.id):
                raise HTTPException(400, "该手机号已被绑定")
            auths = self.users.get_auths_by_user(user_id)
            phone_auth = next((a for a in auths if a.identity_type == "phone"), None)
            if phone_auth:
                self.users.update_auth_identifier(phone_auth, new_phone)
            else:
                credential = auths[0].credential if auths else None
                self.users.create_auth(user_id, "phone", new_phone, credential)

        return self.users.update(user, payload)

    def get_or_404(self, user_id: str) -> User:
        user = self.users.get(user_id)
        if not user:
            raise HTTPException(404, "用户不存在")
        return user

    def delete(self, user_id: str) -> None:
        user = self.get_or_404(user_id)
        self.users.delete(user)

    def register_user(self, username: str, password: str, display_name: str = "智颜用户") -> User:
        """用户注册：账号查重后加盐散列密码并写入双表"""
        is_phone = bool(re.match(r'^(?:1[3-9]\d{9}|\d{11})$', username))
        identity_type = "phone" if is_phone else "username"
        
        existing_auth = self.users.get_auth(identity_type, username)
        if existing_auth:
            raise HTTPException(400, "该账号已被注册")

        if display_name == "智颜用户" or not display_name:
            final_display_name = "" if is_phone else username
        else:
            final_display_name = display_name

        # 1. 新建核心 User 账号主体
        user = self.users.create({
            "display_name": final_display_name,
            "login_type": "phone" if is_phone else "username",
            "phone": username if is_phone else None
        })

        if is_phone and not final_display_name:
            user_id_str = str(user.id).replace('-', '')
            user = self.users.update(user, {"display_name": f"智{user_id_str[:7]}"})

        # 2. 生成安全密码散列值，并写入 user_social_auths 授权映射表中
        password_hash = get_password_hash(password)
        self.users.create_auth(
            user_id=user.id,
            identity_type="phone" if is_phone else "username",
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
            raise HTTPException(404, "账号不存在")

        # 3. 比对加盐哈希值
        if not verify_password(password, auth.credential):
            raise HTTPException(401, "密码错误")

        return auth.user

