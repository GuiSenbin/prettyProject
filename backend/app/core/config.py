"""应用配置：集中读取数据库、AI 和服务环境变量。"""
import os
from pathlib import Path
from functools import lru_cache
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parents[3]
BACKEND_DIR = BASE_DIR / "backend"

load_dotenv(BASE_DIR / ".env.local", override=False)
load_dotenv(BACKEND_DIR / ".env.local", override=True)


class Settings:
    # 数据库
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{BACKEND_DIR}/data/miyang.db")

    # AI（可选）
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_BASE_URL: str = os.getenv("OPENAI_BASE_URL", "")
    AI_MODEL: str = os.getenv("AI_MODEL", "gpt-4o-mini")
    DEEPSEEK_API_KEY: str = os.getenv("DEEPSEEK_API_KEY", "")
    DEEPSEEK_BASE_URL: str = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
    DEEPSEEK_MODEL: str = os.getenv("DEEPSEEK_MODEL", "deepseek-v4-flash")
    DEEPSEEK_TIMEOUT_SECONDS: int = int(os.getenv("DEEPSEEK_TIMEOUT_SECONDS", "18"))
    CHAT_MODEL_DEBUG: bool = os.getenv("CHAT_MODEL_DEBUG", "false").lower() == "true"

    # 服务
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"

    # CORS
    CORS_ORIGINS: list[str] = os.getenv("CORS_ORIGINS", "*").split(",")


@lru_cache()
def get_settings() -> Settings:
    return Settings()
