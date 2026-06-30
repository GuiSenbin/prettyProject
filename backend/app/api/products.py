"""产品百科 API"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import select

from backend.app.core.deps import get_db
from backend.app.models.product import Product
from backend.app.schemas.product import ProductResponse

router = APIRouter(prefix="/products", tags=["产品百科"])


@router.get("/", response_model=list[ProductResponse])
def list_products(
    category: str = Query("all"),
    search: str = Query(""),
    skin_type: str = Query(""),
    db: Session = Depends(get_db),
):
    query = select(Product)
    if category and category != "all":
        query = query.where(Product.category == category)
    if skin_type:
        query = query.where(Product.suitable.contains(skin_type))

    products = db.execute(query).scalars().all()
    result = [p.to_dict() for p in products]

    if search:
        s = search.lower()
        result = [p for p in result
                  if s in p["name"].lower()
                  or s in p["desc"].lower()
                  or s in p["category_name"].lower()]
    return result
