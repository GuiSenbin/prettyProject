"""用户模块模型：定义企业级解耦多端用户与授权表。"""
import datetime
import uuid
from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship
from backend.app.core.database import Base


def generate_uuid() -> str:
    """生成 36 位标准 UUID 字符串作为全局唯一用户号"""
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    phone = Column(String(32), unique=True, nullable=True)  # 实名手机号可空以实现免密体验
    display_name = Column(String(50), nullable=False, default="智颜用户")
    avatar_url = Column(String(255), nullable=True)
    login_type = Column(String(20), nullable=False, default="username")
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    # 关联授权凭证
    auths = relationship("UserAuth", back_populates="user", cascade="all, delete-orphan")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "phone": self.phone,
            "display_name": self.display_name,
            "avatar_url": self.avatar_url,
            "login_type": self.login_type,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class UserAuth(Base):
    __tablename__ = "user_social_auths"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    identity_type = Column(String(20), nullable=False)  # username, phone, wechat, alipay
    identifier = Column(String(100), nullable=False)  # 账号名、手机号、微信unionid等
    credential = Column(String(255), nullable=True)  # 散列密码或AccessToken

    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    user = relationship("User", back_populates="auths")

    __table_args__ = (
        UniqueConstraint("identity_type", "identifier", name="uq_auth_type_identifier"),
    )


