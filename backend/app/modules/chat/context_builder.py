"""AI 问答上下文构建：组装用户档案、产品库和最近会话历史。"""
from sqlalchemy.orm import Session

from backend.app.modules.products.repository import ProductRepository
from backend.app.modules.profiles.repository import ProfileRepository
from backend.app.modules.chat.privacy import sanitize_text


class ChatContextBuilder:
    def __init__(self, db: Session):
        self.profiles = ProfileRepository(db)
        self.products = ProductRepository(db)

    def build(self, user_id: str, session=None) -> dict:
        profile = self.profiles.get_by_user_id(user_id)
        user_products = self.products.list_user_products(user_id)
        messages = list(getattr(session, "messages", []) or [])
        return {
            "profile": profile.to_dict() if profile else None,
            "user_products": [self._serialize_user_product(item) for item in user_products[:12]],
            "recent_messages": [
                {
                    "role": message.role,
                    "content": sanitize_text(message.content_text),
                    "intent": message.intent,
                    "subject_type": message.subject_type,
                }
                for message in messages[-8:]
            ],
        }

    def _serialize_user_product(self, item) -> dict:
        product = item.product
        if not product:
            return {
                "name": item.display_name(),
                "source": item.source,
                "category": None,
                "ingredients": [],
            }
        summary = product.to_summary()
        return {
            "id": product.id,
            "brand": product.brand,
            "name": product.name,
            "category": product.category,
            "ingredients": [
                {
                    "name": ingredient.get("display_name"),
                    "tags": ingredient.get("tags", []),
                    "purposes": ingredient.get("purposes", []),
                    "safety_level": ingredient.get("safety_level"),
                }
                for ingredient in summary.get("ingredients", [])[:20]
            ],
        }
