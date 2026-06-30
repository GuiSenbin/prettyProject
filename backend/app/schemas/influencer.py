"""达人 Schema"""
from pydantic import BaseModel


class InfluencerResponse(BaseModel):
    id: int
    name: str
    tag: str
    category: str
    avatar: str
    banner: str
    title: str
    content: str
    products: list[str]
    bg: str

    model_config = {"from_attributes": True}
