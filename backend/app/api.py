"""API 注册入口：统一挂载业务模块路由。"""
from fastapi import APIRouter
from backend.app.modules.profiles.router import router as profiles_router
from backend.app.modules.products.router import router as products_router
from backend.app.modules.users.router import router as users_router

api_router = APIRouter(prefix="/api")
api_router.include_router(users_router)
api_router.include_router(profiles_router)
api_router.include_router(products_router)
