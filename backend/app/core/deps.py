"""通用依赖注入：暴露 FastAPI 需要的基础依赖。"""
from typing import Generator
from sqlalchemy.orm import Session
from backend.app.core.database import get_db as _get_db


def get_db() -> Generator[Session, None, None]:
    yield from _get_db()
