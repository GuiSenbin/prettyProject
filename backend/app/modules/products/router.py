"""产品库路由：提供本地主库搜索、个人产品库和产品详情入口。"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from backend.app.core.deps import get_db
from backend.app.modules.products.schemas import (
    ProductAnalysis,
    ProductDetail,
    ProductSummary,
    UserProductCreate,
    UserProductResponse,
)
from backend.app.modules.products.service import ProductService
from backend.app.core.schemas import StandardResponse

router = APIRouter(prefix="/products", tags=["产品库"])

@router.get("/search", response_model=StandardResponse[list[ProductSummary]])
def search_products(
    q: str = "",
    page: int = 1,
    size: int = 12,
    db: Session = Depends(get_db),
):
    """根据关键字和品类搜索主库产品。"""
    items = ProductService(db).search_products(q, page, size)
    return {
        "code": 200,
        "message": "success",
        "data": items
    }

@router.get("/my/{user_id}", response_model=StandardResponse[list[UserProductResponse]])
def list_my_products(user_id: str, db: Session = Depends(get_db)):
    """读取用户自己的产品库。"""
    items = ProductService(db).list_my_products(user_id)
    return {
        "code": 200,
        "message": "success",
        "data": items
    }


@router.post("/my/{user_id}", response_model=StandardResponse[UserProductResponse])
def add_my_product(user_id: str, payload: UserProductCreate, db: Session = Depends(get_db)):
    """加入主库产品，或保存一条待完善产品。"""
    item = ProductService(db).add_my_product(user_id, payload)
    return {
        "code": 200,
        "message": "success",
        "data": item
    }


@router.delete("/my/{user_id}/{user_product_id}", response_model=StandardResponse[dict])
def delete_my_product(user_id: str, user_product_id: int, db: Session = Depends(get_db)):
    """从用户自己的产品库移除一条产品记录，不删除主产品库产品。"""
    ProductService(db).delete_my_product(user_id, user_product_id)
    return {
        "code": 200,
        "message": "success",
        "data": {"deleted": True}
    }


@router.get("/{product_id}", response_model=StandardResponse[ProductDetail])
def get_product_detail(product_id: int, user_id: str | None = None, db: Session = Depends(get_db)):
    """读取产品详情：产品事实、成分功效分组、安全提示和个人适配分析。"""
    detail = ProductService(db).get_detail(product_id, user_id)
    return {
        "code": 200,
        "message": "success",
        "data": detail
    }


@router.get("/{product_id}/analysis", response_model=StandardResponse[ProductAnalysis])
def analyze_product(product_id: int, user_id: str | None = None, db: Session = Depends(get_db)):
    """结合用户个人档案返回轻量成分匹配结论。"""
    analysis = ProductService(db).analyze(product_id, user_id)
    return {
        "code": 200,
        "message": "success",
        "data": analysis
    }
