"""产品库 API 测试：验证主库搜索、个人产品库和基础匹配分析。"""
import unittest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.api import api_router
from backend.app.core.database import Base
from backend.app.core.deps import get_db
from backend.app.modules.products.models import Ingredient, Product, ProductIngredient
from backend.app.modules.users.models import User
from backend.app.modules.profiles.models import UserProfile


def auth_headers(user_id: str) -> dict[str, str]:
    return {"Authorization": f"Bearer token-{user_id}-123456"}


def make_client():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    test_app = FastAPI()
    test_app.include_router(api_router)
    test_app.dependency_overrides[get_db] = override_get_db
    return TestClient(test_app), TestingSessionLocal


def api_data(response):
    return response.json()["data"]


class ProductApiTest(unittest.TestCase):
    def test_product_search_returns_verified_official_product_and_empty_results(self):
        client, _ = make_client()

        hit_response = client.get("/api/products/search", params={"q": "CeraVe"})
        self.assertEqual(hit_response.status_code, 200)
        hits = api_data(hit_response)
        self.assertGreaterEqual(len(hits), 1)
        cerave = next(item for item in hits if item["brand"] == "CeraVe")
        self.assertEqual(cerave["status"], "verified")
        self.assertEqual(cerave["source"], "brand-official")
        self.assertIsNone(cerave["registration_number"])
        self.assertEqual(cerave["brand_origin_country"], "美国")
        self.assertIn("cerave.com", cerave["source_url"])
        self.assertTrue(cerave["has_ingredients"])

        miss_response = client.get("/api/products/search", params={"q": "完全不存在的产品"})
        self.assertEqual(miss_response.status_code, 200)
        self.assertEqual(api_data(miss_response), [])

    def test_product_search_returns_official_niacinamide_with_analysis_highlight(self):
        client, session_factory = make_client()
        with session_factory() as db:
            user = User(display_name="测试用户", login_type="username")
            db.add(user)
            db.commit()
            db.refresh(user)
            user_id = user.id

        search_response = client.get("/api/products/search", params={"q": "The Ordinary Niacinamide"})

        self.assertEqual(search_response.status_code, 200)
        product = api_data(search_response)[0]
        self.assertEqual(product["brand"], "The Ordinary")
        self.assertEqual(product["status"], "verified")
        self.assertTrue(product["has_ingredients"])

        analysis = client.get(f"/api/products/{product['id']}/analysis", headers=auth_headers(user_id))
        self.assertEqual(analysis.status_code, 200)
        highlight_names = [item["inci_name"] for item in api_data(analysis)["highlights"]]
        self.assertIn("NIACINAMIDE", highlight_names)

    def test_product_search_returns_common_brand_candidates(self):
        client, _ = make_client()

        response = client.get("/api/products/search", params={"q": "修丽可"})

        self.assertEqual(response.status_code, 200)
        hits = api_data(response)
        self.assertGreaterEqual(len(hits), 1)
        self.assertEqual(hits[0]["brand"], "修丽可")
        self.assertEqual(hits[0]["status"], "verified")
        self.assertTrue(hits[0]["has_ingredients"])
        self.assertIn("skinceuticals.com.au", hits[0]["source_url"])
        self.assertIn("skinceuticals.com.au", hits[0]["image_url"])
        ingredient_names = [item["inci_name"] for item in hits[0]["ingredients"]]
        self.assertIn("ASCORBIC ACID", ingredient_names)
        self.assertIn("FERULIC ACID", ingredient_names)
        self.assertIn("抗氧化", hits[0]["benefit_tags"])

    def test_product_search_ignores_category_query_and_returns_benefit_tags(self):
        client, session_factory = make_client()
        with session_factory() as db:
            brightening = Ingredient(
                inci_name="TEST NIACINAMIDE",
                zh_name="测试烟酰胺",
                tags=["brightening"],
            )
            anti_aging = Ingredient(
                inci_name="TEST RETINOL",
                zh_name="测试视黄醇",
                tags=["anti_aging"],
            )
            serum = Product(
                brand="Shared Test Brand",
                name="Shared Test Brightening Serum",
                category="精华",
                status="verified",
                source="test",
            )
            cream = Product(
                brand="Shared Test Brand",
                name="Shared Test Anti Aging Cream",
                category="乳液/面霜",
                status="verified",
                source="test",
            )
            db.add_all([brightening, anti_aging, serum, cream])
            db.flush()
            db.add_all([
                ProductIngredient(product_id=serum.id, ingredient_id=brightening.id, position=1),
                ProductIngredient(product_id=cream.id, ingredient_id=anti_aging.id, position=1),
            ])
            db.commit()

        response = client.get("/api/products/search", params={"q": "Shared Test Brand", "category": "精华"})

        self.assertEqual(response.status_code, 200)
        hits = api_data(response)
        categories = {item["category"] for item in hits}
        self.assertIn("精华", categories)
        self.assertIn("乳液/面霜", categories)
        self.assertTrue(all("ingredient_count" in item for item in hits))
        self.assertTrue(any("美白/提亮" in item["benefit_tags"] for item in hits))
        self.assertTrue(any("抗老" in item["benefit_tags"] for item in hits))

    def test_product_summary_derives_benefit_tags_from_ingredient_purposes(self):
        client, session_factory = make_client()
        with session_factory() as db:
            niacinamide = Ingredient(
                inci_name="PURPOSE ONLY NIACINAMIDE",
                zh_name="目的烟酰胺",
                tags=[],
                purposes=["美白", "抗氧化"],
            )
            product = Product(
                brand="Purpose Lab",
                name="Purpose Benefit Serum",
                category="精华",
                status="verified",
                source="test",
            )
            db.add_all([niacinamide, product])
            db.flush()
            db.add(ProductIngredient(product_id=product.id, ingredient_id=niacinamide.id, position=1))
            db.commit()

        response = client.get("/api/products/search", params={"q": "Purpose Benefit Serum"})

        self.assertEqual(response.status_code, 200)
        product = api_data(response)[0]
        self.assertEqual(product["benefit_tags"], ["抗氧化", "美白/提亮"])

    def test_product_summary_hides_generic_cleaning_and_limits_display_benefits(self):
        client, session_factory = make_client()
        with session_factory() as db:
            cleanser = Ingredient(
                inci_name="PURPOSE ONLY CLEANSER",
                zh_name="目的清洁剂",
                tags=[],
                purposes=["清洁"],
            )
            moisturizing = Ingredient(
                inci_name="PURPOSE ONLY HUMECTANT",
                zh_name="目的保湿剂",
                tags=[],
                purposes=["保湿"],
            )
            repair = Ingredient(
                inci_name="PURPOSE ONLY REPAIR",
                zh_name="目的修护剂",
                tags=[],
                purposes=["修护"],
            )
            antioxidant = Ingredient(
                inci_name="PURPOSE ONLY ANTIOXIDANT",
                zh_name="目的抗氧化剂",
                tags=[],
                purposes=["抗氧化"],
            )
            brightening = Ingredient(
                inci_name="PURPOSE ONLY BRIGHTENING",
                zh_name="目的美白剂",
                tags=[],
                purposes=["美白"],
            )
            cleansing_product = Product(
                brand="Purpose Lab",
                name="Purpose Cleanser",
                category="洁面",
                status="verified",
                source="test",
            )
            serum = Product(
                brand="Purpose Lab",
                name="Purpose Multi Benefit Serum",
                category="精华",
                status="verified",
                source="test",
            )
            db.add_all([cleanser, moisturizing, repair, antioxidant, brightening, cleansing_product, serum])
            db.flush()
            db.add(ProductIngredient(product_id=cleansing_product.id, ingredient_id=cleanser.id, position=1))
            db.add_all([
                ProductIngredient(product_id=serum.id, ingredient_id=moisturizing.id, position=1),
                ProductIngredient(product_id=serum.id, ingredient_id=repair.id, position=2),
                ProductIngredient(product_id=serum.id, ingredient_id=antioxidant.id, position=3),
                ProductIngredient(product_id=serum.id, ingredient_id=brightening.id, position=4),
            ])
            db.commit()

        cleanser_response = client.get("/api/products/search", params={"q": "Purpose Cleanser"})
        serum_response = client.get("/api/products/search", params={"q": "Purpose Multi Benefit Serum"})

        self.assertEqual(cleanser_response.status_code, 200)
        self.assertEqual(api_data(cleanser_response)[0]["benefit_tags"], [])
        self.assertEqual(serum_response.status_code, 200)
        self.assertEqual(api_data(serum_response)[0]["benefit_tags"], ["修护", "抗氧化"])

    def test_product_detail_returns_analysis_benefits_and_safety_groups(self):
        client, session_factory = make_client()
        with session_factory() as db:
            user = User(display_name="敏感肌用户", login_type="username")
            db.add(user)
            db.commit()
            db.refresh(user)
            db.add(
                UserProfile(
                    user_id=user.id,
                    gender="female",
                    age=29,
                    skin_type="敏感肌",
                    skin_concerns=["泛红"],
                )
            )
            db.commit()
            user_id = user.id

        product_id = api_data(client.get("/api/products/search", params={"q": "修丽可 CE"}))[0]["id"]
        response = client.get(f"/api/products/{product_id}", headers=auth_headers(user_id))

        self.assertEqual(response.status_code, 200)
        detail = api_data(response)
        self.assertEqual(detail["product"]["brand"], "修丽可")
        self.assertGreaterEqual(detail["product"]["ingredient_count"], 12)
        first_ingredient = detail["product"]["ingredients"][0]
        self.assertIn("safety_level", first_ingredient)
        self.assertIn("purposes", first_ingredient)
        self.assertIn("抗氧化", [group["name"] for group in detail["benefit_groups"]])
        self.assertIn("酸类/高活性", [group["name"] for group in detail["safety_groups"]])
        self.assertEqual(detail["analysis"]["status"], "caution")
        self.assertIn("敏感肌", "".join(detail["analysis"]["reasons"]))

    def test_user_can_add_master_product_and_pending_product(self):
        client, session_factory = make_client()
        with session_factory() as db:
            user = User(display_name="测试用户", login_type="username")
            db.add(user)
            db.commit()
            db.refresh(user)
            user_id = user.id

        search_response = client.get("/api/products/search", params={"q": "Anthelios Melt-In Milk"})
        product_id = api_data(search_response)[0]["id"]

        add_master = client.post("/api/products/my", headers=auth_headers(user_id), json={"product_id": product_id})
        self.assertEqual(add_master.status_code, 200)
        added_master = api_data(add_master)
        self.assertEqual(added_master["product"]["id"], product_id)
        self.assertGreater(len(added_master["product"]["ingredients"]), 0)
        self.assertEqual(added_master["analysis"]["status"], "caution")

        add_pending = client.post("/api/products/my", headers=auth_headers(user_id), json={"name": "我新买的未知精华"})
        self.assertEqual(add_pending.status_code, 200)
        added_pending = api_data(add_pending)
        self.assertEqual(added_pending["status"], "pending")
        self.assertEqual(added_pending["analysis"]["status"], "incomplete")

        my_products = client.get("/api/products/my", headers=auth_headers(user_id))
        self.assertEqual(my_products.status_code, 200)
        self.assertEqual(len(api_data(my_products)), 2)

    def test_user_can_delete_product_from_personal_cabinet(self):
        client, session_factory = make_client()
        with session_factory() as db:
            user = User(display_name="测试用户", login_type="username")
            db.add(user)
            db.commit()
            db.refresh(user)
            user_id = user.id

        product_id = api_data(client.get("/api/products/search", params={"q": "Anthelios Melt-In Milk"}))[0]["id"]
        added = api_data(client.post("/api/products/my", headers=auth_headers(user_id), json={"product_id": product_id}))

        delete_response = client.delete(f"/api/products/my/{added['id']}", headers=auth_headers(user_id))

        self.assertEqual(delete_response.status_code, 200)
        self.assertTrue(api_data(delete_response)["deleted"])
        my_products = client.get("/api/products/my", headers=auth_headers(user_id))
        self.assertEqual(api_data(my_products), [])
        product_detail = client.get(f"/api/products/{product_id}", headers=auth_headers(user_id))
        self.assertEqual(product_detail.status_code, 200)

    def test_sensitive_profile_flags_high_position_alcohol_as_caution(self):
        client, session_factory = make_client()
        with session_factory() as db:
            user = User(display_name="敏感肌用户", login_type="username")
            db.add(user)
            db.commit()
            db.refresh(user)
            db.add(
                UserProfile(
                    user_id=user.id,
                    gender="female",
                    age=28,
                    skin_type="敏感肌",
                    skin_concerns=["泛红"],
                    known_allergies="酒精不耐受",
                )
            )
            db.commit()
            user_id = user.id

        product_id = api_data(client.get("/api/products/search", params={"q": "Anthelios Melt-In Milk"}))[0]["id"]
        analysis = client.get(f"/api/products/{product_id}/analysis", headers=auth_headers(user_id))

        self.assertEqual(analysis.status_code, 200)
        data = api_data(analysis)
        self.assertEqual(data["status"], "avoid")
        self.assertIn("酒精", "".join(data["reasons"]))

    def test_sensitive_profile_flags_official_retinol_product_as_caution(self):
        client, session_factory = make_client()
        with session_factory() as db:
            user = User(display_name="敏感肌用户", login_type="username")
            db.add(user)
            db.commit()
            db.refresh(user)
            db.add(
                UserProfile(
                    user_id=user.id,
                    gender="female",
                    age=31,
                    skin_type="敏感肌",
                    skin_concerns=["泛红"],
                )
            )
            db.commit()
            user_id = user.id

        product_id = api_data(client.get("/api/products/search", params={"q": "Retinol 0.2"}))[0]["id"]
        analysis = client.get(f"/api/products/{product_id}/analysis", headers=auth_headers(user_id))

        self.assertEqual(analysis.status_code, 200)
        data = api_data(analysis)
        self.assertEqual(data["status"], "caution")
        self.assertIn("视黄醇", "".join(data["reasons"]))

    def test_product_without_ingredients_returns_incomplete_analysis(self):
        client, session_factory = make_client()
        with session_factory() as db:
            user = User(display_name="普通用户", login_type="username")
            db.add(user)
            db.commit()
            db.refresh(user)
            user_id = user.id

        add_pending = client.post("/api/products/my", headers=auth_headers(user_id), json={"name": "未知面霜"})
        analysis = api_data(add_pending)["analysis"]

        self.assertEqual(analysis["status"], "incomplete")
        self.assertEqual(analysis["summary"], "缺少成分，无法分析")

    def test_my_products_uses_authenticated_user_not_path_user_id(self):
        client, session_factory = make_client()
        with session_factory() as db:
            owner = User(display_name="本人", login_type="username")
            other = User(display_name="其他人", login_type="username")
            db.add_all([owner, other])
            db.commit()
            db.refresh(owner)
            db.refresh(other)
            owner_id = owner.id
            other_id = other.id

        product_id = api_data(client.get("/api/products/search", params={"q": "Anthelios Melt-In Milk"}))[0]["id"]
        add_response = client.post("/api/products/my", headers=auth_headers(owner_id), json={"product_id": product_id})
        self.assertEqual(add_response.status_code, 200)

        owner_products = client.get("/api/products/my", headers=auth_headers(owner_id))
        other_products = client.get("/api/products/my", headers=auth_headers(other_id))

        self.assertEqual(len(api_data(owner_products)), 1)
        self.assertEqual(api_data(other_products), [])

if __name__ == "__main__":
    unittest.main()
