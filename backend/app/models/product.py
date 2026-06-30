"""产品数据模型"""
from sqlalchemy import Column, Integer, String, Text, JSON
from backend.app.database import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    icon = Column(String(10), default="📦")
    category = Column(String(30), nullable=False)
    category_name = Column(String(30), default="")
    desc = Column(Text, default="")
    skin_tags = Column(JSON, default=list)
    suitable = Column(JSON, default=list)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "icon": self.icon,
            "category": self.category,
            "category_name": self.category_name,
            "desc": self.desc,
            "skin_tags": self.skin_tags or [],
            "suitable": self.suitable or [],
        }
