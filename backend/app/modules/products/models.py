"""产品模块模型：定义全站产品主库、成分库和用户产品库。"""
import datetime
from sqlalchemy import Column, DateTime, ForeignKey, Integer, JSON, String, Text, UniqueConstraint
from sqlalchemy.orm import relationship
from backend.app.core.database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    brand = Column(String(80), nullable=True)
    name = Column(String(160), nullable=False, index=True)
    category = Column(String(40), nullable=True)
    image_url = Column(String(255), nullable=True)
    registration_number = Column(String(80), nullable=True)
    brand_origin_country = Column(String(40), nullable=True)
    status = Column(String(24), nullable=False, default="verified")
    source = Column(String(40), nullable=False, default="seed")
    ingredient_source = Column(String(80), nullable=True)
    source_url = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    ingredients = relationship(
        "ProductIngredient",
        back_populates="product",
        cascade="all, delete-orphan",
        order_by="ProductIngredient.position",
    )

    def to_summary(self) -> dict:
        return {
            "id": self.id,
            "brand": self.brand,
            "name": self.name,
            "category": self.category,
            "image_url": self.image_url,
            "registration_number": self.registration_number,
            "brand_origin_country": self.brand_origin_country,
            "status": self.status,
            "source": self.source,
            "ingredient_source": self.ingredient_source,
            "source_url": self.source_url,
            "has_ingredients": bool(self.ingredients),
            "ingredients": [
                item.ingredient.to_dict(item.position)
                for item in (self.ingredients or [])
                if item.ingredient
            ],
        }


class Ingredient(Base):
    __tablename__ = "ingredients"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    inci_name = Column(String(120), nullable=False, unique=True, index=True)
    zh_name = Column(String(120), nullable=False)
    aliases = Column(JSON, nullable=False, default=list)
    tags = Column(JSON, nullable=False, default=list)
    description = Column(Text, nullable=True)
    safety_level = Column(String(40), nullable=True, default="unknown")
    purposes = Column(JSON, nullable=False, default=list)
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    def display_name(self) -> str:
        return self.zh_name or self.inci_name

    def to_dict(self, position: int | None = None) -> dict:
        return {
            "id": self.id,
            "inci_name": self.inci_name,
            "zh_name": self.zh_name,
            "display_name": self.display_name(),
            "aliases": self.aliases or [],
            "tags": self.tags or [],
            "description": self.description,
            "safety_level": self.safety_level,
            "purposes": self.purposes or [],
            "position": position,
        }


class ProductIngredient(Base):
    __tablename__ = "product_ingredients"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), nullable=False)
    ingredient_id = Column(Integer, ForeignKey("ingredients.id", ondelete="CASCADE"), nullable=False)
    position = Column(Integer, nullable=False)
    concentration_hint = Column(String(32), nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.now)

    product = relationship("Product", back_populates="ingredients")
    ingredient = relationship("Ingredient")

    __table_args__ = (
        UniqueConstraint("product_id", "ingredient_id", name="uq_product_ingredient"),
        UniqueConstraint("product_id", "position", name="uq_product_ingredient_position"),
    )


class UserProduct(Base):
    __tablename__ = "user_products"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(String(36), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="SET NULL"), nullable=True)
    custom_name = Column(String(160), nullable=True)
    status = Column(String(24), nullable=False, default="active")
    source = Column(String(32), nullable=False, default="manual")
    notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.datetime.now)
    updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

    product = relationship("Product")

    def display_name(self) -> str:
        if self.product:
            return self.product.name
        return self.custom_name or "待完善产品"
