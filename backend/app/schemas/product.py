"""产品 Schema"""
from pydantic import BaseModel


class ProductResponse(BaseModel):
    id: int
    name: str
    icon: str
    category: str
    category_name: str
    desc: str
    skin_tags: list[str]
    suitable: list[str]

    model_config = {"from_attributes": True}
