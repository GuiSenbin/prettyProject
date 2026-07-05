"""应用配置：集中读取数据库、AI 和服务环境变量。"""
import os
from pathlib import Path
from functools import lru_cache

BASE_DIR = Path(__file__).resolve().parents[3]


class Settings:
    # 数据库
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{BASE_DIR}/backend/data/miyang.db")

    # OpenAI（可选）
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_BASE_URL: str = os.getenv("OPENAI_BASE_URL", "")
    AI_MODEL: str = os.getenv("AI_MODEL", "gpt-4o-mini")

    # 服务
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"

    # CORS
    CORS_ORIGINS: list[str] = os.getenv("CORS_ORIGINS", "*").split(",")


@lru_cache()
def get_settings() -> Settings:
    return Settings()
