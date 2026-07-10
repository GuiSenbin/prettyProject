"""FastAPI 应用入口：注册中间件、生命周期和全局健康检查。"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

from backend.app.api import api_router
from backend.app.core.config import get_settings
from backend.app.core.database import init_db

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
logger = logging.getLogger(__name__)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🚀 智颜后端启动中...")
    init_db()
    logger.info("✅ 数据库就绪")
    yield
    logger.info("👋 服务关闭")


app = FastAPI(
    title="智颜 API",
    description="用算力解析肌理状态，以光影重塑面部轮廓",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)

os.makedirs("backend/static/avatars", exist_ok=True)
app.mount("/static", StaticFiles(directory="backend/static"), name="static")


@app.get("/")
def root():
    return {
        "service": "智颜 API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/health",
    }


@app.get("/api/health")
def health():
    return {"status": "ok", "service": "智颜"}
