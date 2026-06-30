"""API 路由统一注册"""
from fastapi import APIRouter
from backend.app.api import users, chat, products, influencers

api_router = APIRouter(prefix="/api")
api_router.include_router(users.router)
api_router.include_router(chat.router)
api_router.include_router(products.router)
api_router.include_router(influencers.router)
