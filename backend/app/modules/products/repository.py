"""产品模块仓储：封装产品主库、成分和用户产品库数据库读写。"""
import re
from sqlalchemy import case, or_, select
from sqlalchemy.orm import Session, selectinload
from backend.app.modules.products.models import (
    Ingredient,
    Product,
    ProductIngredient,
    UserProduct,
)


class ProductRepository:
    def __init__(self, db: Session):
        self.db = db

    def has_products(self) -> bool:
        return self.db.execute(select(Product.id).limit(1)).first() is not None

    def get_product_by_name(self, name: str) -> Product | None:
        return self.db.execute(select(Product).where(Product.name == name)).scalar_one_or_none()

    def list_dirty_seed_products(self) -> list[Product]:
        return self.db.execute(
            select(Product).where(Product.brand == "智颜示例", Product.source == "seed")
        ).scalars().all()

    def search(self, query: str, skip: int = 0, limit: int = 12) -> list[Product]:
        tokens = [query]
        compact = query.replace(" ", "")
        ascii_terms = re.findall(r"[A-Za-z0-9][A-Za-z0-9%+.-]*", query)
        if ascii_terms:
            tokens.extend(term for term in ascii_terms if len(term) >= 4)
        elif len(compact) > 2:
            tokens.extend([compact[:2], compact[-2:]])
        conditions = []
        for token in dict.fromkeys(token for token in tokens if token):
            pattern = f"%{token}%"
            conditions.append(or_(Product.name.like(pattern), Product.brand.like(pattern), Product.category.like(pattern)))
        exact_pattern = f"%{query}%"
        relevance = case(
            (Product.name.like(exact_pattern), 0),
            (Product.brand.like(exact_pattern), 1),
            (Product.category.like(exact_pattern), 2),
            else_=3,
        )
        stmt = (
            select(Product)
            .options(selectinload(Product.ingredients).selectinload(ProductIngredient.ingredient))
            .offset(skip)
            .limit(limit)
        )
        if conditions:
            stmt = stmt.where(or_(*conditions))
        if query:
            stmt = stmt.order_by(relevance.asc(), Product.id.asc())
        else:
            stmt = stmt.order_by(Product.category.asc(), Product.brand.asc(), Product.name.asc())
        return self.db.execute(stmt).scalars().all()

    def get_product(self, product_id: int) -> Product | None:
        return self.db.execute(
            select(Product)
            .options(selectinload(Product.ingredients).selectinload(ProductIngredient.ingredient))
            .where(Product.id == product_id)
        ).scalar_one_or_none()

    def get_ingredient_by_inci(self, inci_name: str) -> Ingredient | None:
        return self.db.execute(select(Ingredient).where(Ingredient.inci_name == inci_name)).scalar_one_or_none()

    def create_ingredient(self, payload: dict) -> Ingredient:
        ingredient = Ingredient(**payload)
        self.db.add(ingredient)
        self.db.flush()
        return ingredient

    def create_product(self, payload: dict) -> Product:
        product = Product(**payload)
        self.db.add(product)
        self.db.flush()
        return product

    def update_product(self, product: Product, payload: dict) -> Product:
        for key, value in payload.items():
            setattr(product, key, value)
        self.db.flush()
        return product

    def clear_product_ingredients(self, product: Product) -> None:
        for item in list(product.ingredients or []):
            self.db.delete(item)
        self.db.flush()

    def delete_product(self, product: Product) -> None:
        self.db.delete(product)
        self.db.flush()

    def attach_ingredient(self, product: Product, ingredient: Ingredient, position: int) -> ProductIngredient:
        item = ProductIngredient(product=product, ingredient=ingredient, position=position)
        self.db.add(item)
        self.db.flush()
        return item

    def list_user_products(self, user_id: str) -> list[UserProduct]:
        return self.db.execute(
            select(UserProduct)
            .options(
                selectinload(UserProduct.product)
                .selectinload(Product.ingredients)
                .selectinload(ProductIngredient.ingredient)
            )
            .where(UserProduct.user_id == user_id)
            .order_by(UserProduct.created_at.desc(), UserProduct.id.desc())
        ).scalars().all()

    def get_user_product(self, user_id: str, user_product_id: int) -> UserProduct | None:
        return self.db.execute(
            select(UserProduct).where(UserProduct.user_id == user_id, UserProduct.id == user_product_id)
        ).scalar_one_or_none()

    def get_user_product_by_product_id(self, user_id: str, product_id: int) -> UserProduct | None:
        return self.db.execute(
            select(UserProduct).where(UserProduct.user_id == user_id, UserProduct.product_id == product_id)
        ).scalar_one_or_none()

    def create_user_product(self, payload: dict) -> UserProduct:
        item = UserProduct(**payload)
        self.db.add(item)
        self.db.commit()
        self.db.refresh(item)
        if item.product_id:
            item.product = self.get_product(item.product_id)
        return item

    def delete_user_product(self, item: UserProduct) -> None:
        self.db.delete(item)
        self.db.commit()

    def commit(self) -> None:
        self.db.commit()
