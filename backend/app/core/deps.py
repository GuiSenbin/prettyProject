"""通用依赖注入：暴露 FastAPI 需要的基础依赖。"""
from typing import Generator
from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import Session
from backend.app.core.database import get_db as _get_db
from backend.app.modules.users.repository import UserRepository


def get_db() -> Generator[Session, None, None]:
    yield from _get_db()


def get_current_user_id(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> str:
    """从当前本地登录 token 解析用户 ID，供需要登录主体的接口使用。"""
    if not authorization or not authorization.startswith("Bearer token-"):
        raise HTTPException(status_code=401, detail="请先登录")
    token_body = authorization.removeprefix("Bearer token-")
    user_id, separator, _timestamp = token_body.rpartition("-")
    if not separator or not user_id:
        raise HTTPException(status_code=401, detail="登录状态无效")
    if not UserRepository(db).get(user_id):
        raise HTTPException(status_code=401, detail="登录用户不存在")
    return user_id
