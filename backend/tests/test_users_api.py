"""用户 API 测试：验证当前登录用户资料接口。"""
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


def auth_headers(user_id: str) -> dict[str, str]:
    return {"Authorization": f"Bearer token-{user_id}-123456"}


def api_data(response):
    return response.json()["data"]


class UserApiTest(unittest.TestCase):
    def test_user_me_reads_and_updates_authenticated_user(self):
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

        read_response = client.get("/api/users/me", headers=auth_headers(owner_id))
        self.assertEqual(read_response.status_code, 200)
        self.assertEqual(api_data(read_response)["display_name"], "本人")

        update_response = client.put(
            "/api/users/me",
            headers=auth_headers(owner_id),
            json={"display_name": "新的本人"},
        )
        self.assertEqual(update_response.status_code, 200)
        self.assertEqual(api_data(update_response)["display_name"], "新的本人")

        other_response = client.get("/api/users/me", headers=auth_headers(other_id))
        self.assertEqual(api_data(other_response)["display_name"], "其他人")


if __name__ == "__main__":
    unittest.main()
