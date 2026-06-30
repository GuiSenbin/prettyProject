"""美妆达人模型"""
from sqlalchemy import Column, Integer, String, Text, JSON
from backend.app.database import Base


class Influencer(Base):
    __tablename__ = "influencers"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    tag = Column(String(30), default="")
    category = Column(String(30), default="")   # makeup / skincare / review
    avatar = Column(String(10), default="👤")
    banner = Column(String(10), default="✨")
    title = Column(String(100), default="")
    content = Column(Text, default="")
    products = Column(JSON, default=list)
    bg = Column(String(200), default="")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "name": self.name,
            "tag": self.tag,
            "category": self.category,
            "avatar": self.avatar,
            "banner": self.banner,
            "title": self.title,
            "content": self.content,
            "products": self.products or [],
            "bg": self.bg,
        }
