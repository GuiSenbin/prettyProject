"""系统通用 Pydantic 数据规范：提供统一标准响应泛型实体。"""
from typing import Generic, TypeVar
from pydantic import BaseModel

T = TypeVar('T')

class StandardResponse(BaseModel, Generic[T]):
    code: int = 200
    message: str = "success"
    data: T
