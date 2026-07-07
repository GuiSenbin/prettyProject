"""个人档案 API 测试：验证档案保存、更新和回显。"""
import unittest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.api import api_router
from backend.app.core.database import Base
from backend.app.core.deps import get_db
from backend.app.modules.users.models import User


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


class ProfileApiTest(unittest.TestCase):
    def test_profile_can_be_saved_and_read_back(self):
        client, session_factory = make_client()
        with session_factory() as db:
            user = User(display_name="测试用户", login_type="username")
            db.add(user)
            db.commit()
            db.refresh(user)
            user_id = user.id

        empty_response = client.get(f"/api/profiles/{user_id}")
        self.assertEqual(empty_response.status_code, 200)
        self.assertIsNone(empty_response.json())

        payload = {
            "gender": "female",
            "age": 28,
            "skin_type": "混合性",
            "skin_tone": "自然偏白",
            "face_shape": "鹅蛋脸",
            "skin_concerns": ["痘痘", "泛红"],
            "known_allergies": "酒精不耐受",
            "period_acne": True,
            "last_period_start": "2026-07-01",
            "cycle_length_days": 30,
            "pregnancy_status": "未怀孕",
            "preference_notes": "讨厌浓香精味，最近熬夜较多",
        }

        save_response = client.put(f"/api/profiles/{user_id}", json=payload)
        self.assertEqual(save_response.status_code, 200)
        saved = save_response.json()
        self.assertEqual(saved["user_id"], user_id)
        self.assertEqual(saved["face_shape"], "鹅蛋脸")
        self.assertEqual(saved["skin_concerns"], ["痘痘", "泛红"])

        read_response = client.get(f"/api/profiles/{user_id}")
        self.assertEqual(read_response.status_code, 200)
        self.assertEqual(read_response.json()["preference_notes"], "讨厌浓香精味，最近熬夜较多")


if __name__ == "__main__":
    unittest.main()
