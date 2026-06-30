"""通用依赖注入"""
from typing import Generator
from sqlalchemy.orm import Session
from backend.app.database import get_db as _get_db


def get_db() -> Generator[Session, None, None]:
    yield from _get_db()
