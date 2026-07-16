"""AI 问答 API 测试：验证多会话、历史回看、重命名和软删除。"""
import unittest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.api import api_router
from backend.app.core.database import Base
from backend.app.core.deps import get_db
from backend.app.modules.chat.models import ChatQuestionLog
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


def api_data(response):
    return response.json()["data"]


def auth_headers(user_id: str) -> dict[str, str]:
    return {"Authorization": f"Bearer token-{user_id}-123456"}


class ChatApiTest(unittest.TestCase):
    def test_first_message_creates_session_with_title_and_persisted_messages(self):
        client, session_factory = make_client()
        with session_factory() as db:
            user = User(display_name="测试用户", login_type="username")
            db.add(user)
            db.commit()
            db.refresh(user)
            user_id = user.id

        response = client.post(
            "/api/chat/messages",
            headers=auth_headers(user_id),
            json={"message": "我最近额头长痘怎么办？"},
        )

        self.assertEqual(response.status_code, 200)
        data = api_data(response)
        self.assertEqual(data["session"]["title"], "额头长痘怎么办")
        self.assertEqual(data["session"]["title_edited"], False)
        self.assertEqual(data["message"]["role"], "assistant")
        self.assertEqual(data["user_message"]["role"], "user")
        self.assertEqual(data["message"]["structured_payload"]["source"], "local_rule")
        self.assertGreaterEqual(len(data["message"]["structured_payload"]["sections"]), 1)

        detail = client.get(f"/api/chat/sessions/{data['session']['id']}", headers=auth_headers(user_id))
        self.assertEqual(detail.status_code, 200)
        messages = api_data(detail)["messages"]
        self.assertEqual([item["role"] for item in messages], ["user", "assistant"])
        self.assertEqual(messages[0]["content_text"], "我最近额头长痘怎么办？")

    def test_session_history_limits_to_recent_ten_and_ignores_deleted(self):
        client, session_factory = make_client()
        with session_factory() as db:
            user = User(display_name="测试用户", login_type="username")
            db.add(user)
            db.commit()
            db.refresh(user)
            user_id = user.id

        created_ids = []
        for index in range(12):
            response = client.post(
                "/api/chat/messages",
                headers=auth_headers(user_id),
                json={"message": f"第{index}个护肤问题怎么处理？"},
            )
            created_ids.append(api_data(response)["session"]["id"])

        delete_response = client.delete(f"/api/chat/sessions/{created_ids[-1]}", headers=auth_headers(user_id))
        self.assertEqual(delete_response.status_code, 200)

        history = client.get("/api/chat/sessions", headers=auth_headers(user_id))

        self.assertEqual(history.status_code, 200)
        sessions = api_data(history)
        self.assertEqual(len(sessions), 10)
        self.assertNotIn(created_ids[-1], [item["id"] for item in sessions])
        self.assertEqual(sessions[0]["id"], created_ids[-2])

    def test_user_can_rename_session_and_title_is_not_auto_overwritten(self):
        client, session_factory = make_client()
        with session_factory() as db:
            user = User(display_name="测试用户", login_type="username")
            db.add(user)
            db.commit()
            db.refresh(user)
            user_id = user.id

        created = api_data(client.post(
            "/api/chat/messages",
            headers=auth_headers(user_id),
            json={"message": "今天想画一个淡妆"},
        ))
        session_id = created["session"]["id"]

        rename = client.patch(
            f"/api/chat/sessions/{session_id}",
            headers=auth_headers(user_id),
            json={"title": "面试淡妆"},
        )
        self.assertEqual(rename.status_code, 200)
        self.assertEqual(api_data(rename)["title"], "面试淡妆")
        self.assertEqual(api_data(rename)["title_edited"], True)

        follow_up = client.post(
            "/api/chat/messages",
            headers=auth_headers(user_id),
            json={"session_id": session_id, "message": "再自然一点"},
        )
        self.assertEqual(follow_up.status_code, 200)
        self.assertEqual(api_data(follow_up)["session"]["title"], "面试淡妆")

    def test_blank_session_title_is_rejected(self):
        client, session_factory = make_client()
        with session_factory() as db:
            user = User(display_name="测试用户", login_type="username")
            db.add(user)
            db.commit()
            db.refresh(user)
            user_id = user.id

        created = api_data(client.post(
            "/api/chat/messages",
            headers=auth_headers(user_id),
            json={"message": "今天想画一个淡妆"},
        ))
        response = client.patch(
            f"/api/chat/sessions/{created['session']['id']}",
            headers=auth_headers(user_id),
            json={"title": "   "},
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["detail"], "请输入会话标题")

    def test_question_log_keeps_sanitized_text_for_knowledge_base(self):
        client, session_factory = make_client()
        with session_factory() as db:
            user = User(display_name="测试用户", login_type="username")
            db.add(user)
            db.commit()
            db.refresh(user)
            user_id = user.id

        response = client.post(
            "/api/chat/messages",
            headers=auth_headers(user_id),
            json={"message": "我手机号13812345678，2026-07-16长痘怎么办？"},
        )
        self.assertEqual(response.status_code, 200)

        with session_factory() as db:
            log = db.query(ChatQuestionLog).one()
            self.assertNotIn("13812345678", log.raw_question)
            self.assertNotIn("2026-07-16", log.raw_question)
            self.assertEqual(log.raw_question, log.normalized_question)
            self.assertIn("[手机号]", log.normalized_question)
            self.assertIn("[日期]", log.normalized_question)

    def test_default_title_does_not_expose_sensitive_text_and_makeup_intent_wins(self):
        client, session_factory = make_client()
        with session_factory() as db:
            user = User(display_name="测试用户", login_type="username")
            db.add(user)
            db.commit()
            db.refresh(user)
            user_id = user.id

        response = client.post(
            "/api/chat/messages",
            headers=auth_headers(user_id),
            json={"message": "我手机号13812345678，今天想画一个淡妆"},
        )

        self.assertEqual(response.status_code, 200)
        data = api_data(response)
        self.assertNotIn("13812345678", data["session"]["title"])
        self.assertEqual(data["session"]["title"], "今天想画一个淡妆")
        self.assertEqual(data["message"]["intent"], "makeup_look")

    def test_chat_history_uses_authenticated_user_not_client_user_id(self):
        client, session_factory = make_client()
        with session_factory() as db:
            owner = User(display_name="会话主人", login_type="username")
            other = User(display_name="其他用户", login_type="username")
            db.add_all([owner, other])
            db.commit()
            db.refresh(owner)
            db.refresh(other)
            owner_id = owner.id
            other_id = other.id

        created = api_data(client.post(
            "/api/chat/messages",
            headers=auth_headers(owner_id),
            json={"message": "我最近泛红怎么办？"},
        ))
        session_id = created["session"]["id"]

        forbidden_detail = client.get(f"/api/chat/sessions/{session_id}", headers=auth_headers(other_id))
        forbidden_delete = client.delete(f"/api/chat/sessions/{session_id}", headers=auth_headers(other_id))
        unauthenticated = client.get("/api/chat/sessions")

        self.assertEqual(forbidden_detail.status_code, 404)
        self.assertEqual(forbidden_delete.status_code, 404)
        self.assertEqual(unauthenticated.status_code, 401)

    def test_unrelated_career_question_is_redirected_to_beauty_scope(self):
        client, session_factory = make_client()
        with session_factory() as db:
            user = User(display_name="测试用户", login_type="username")
            db.add(user)
            db.commit()
            db.refresh(user)
            user_id = user.id

        response = client.post(
            "/api/chat/messages",
            headers=auth_headers(user_id),
            json={"message": "我想转行做程序员，你觉得怎么样？"},
        )

        self.assertEqual(response.status_code, 200)
        payload = api_data(response)["message"]["structured_payload"]
        self.assertEqual(payload["intent"], "out_of_scope")
        self.assertEqual(payload["title"], "这个问题先不展开")
        self.assertIn("美妆", payload["summary"])
        self.assertIn("护肤", payload["summary"])
        self.assertEqual(payload["sections"][0]["type"], "redirect")
        self.assertFalse(payload["context_used"]["profile"])

    def test_other_person_question_uses_general_advice_not_user_profile(self):
        client, session_factory = make_client()
        with session_factory() as db:
            user = User(display_name="测试用户", login_type="username")
            db.add(user)
            db.commit()
            db.refresh(user)
            user_id = user.id

        response = client.post(
            "/api/chat/messages",
            headers=auth_headers(user_id),
            json={"message": "我妈妈最近脸泛红刺痛，可以怎么护肤？"},
        )

        self.assertEqual(response.status_code, 200)
        payload = api_data(response)["message"]["structured_payload"]
        self.assertEqual(payload["subject_type"], "other_person")
        self.assertTrue(payload["context_used"]["profile"] is False)
        self.assertIn("不套用你的个人档案", payload["sections"][0]["body"])

    def test_pregnancy_question_gets_safety_first_answer(self):
        client, session_factory = make_client()
        with session_factory() as db:
            user = User(display_name="测试用户", login_type="username")
            db.add(user)
            db.commit()
            db.refresh(user)
            user_id = user.id

        response = client.post(
            "/api/chat/messages",
            headers=auth_headers(user_id),
            json={"message": "我怀孕了还能用含视黄醇的抗老精华吗？"},
        )

        self.assertEqual(response.status_code, 200)
        payload = api_data(response)["message"]["structured_payload"]
        self.assertEqual(payload["intent"], "pregnancy_safety")
        self.assertEqual(payload["subject_type"], "hypothetical")
        self.assertIn("孕期", payload["title"])
        self.assertIn("视黄醇", payload["safety_note"])

    def test_makeup_question_returns_makeup_specific_steps(self):
        client, session_factory = make_client()
        with session_factory() as db:
            user = User(display_name="测试用户", login_type="username")
            db.add(user)
            db.commit()
            db.refresh(user)
            user_id = user.id

        response = client.post(
            "/api/chat/messages",
            headers=auth_headers(user_id),
            json={"message": "今天面试想画一个清透淡妆，怎么安排？"},
        )

        self.assertEqual(response.status_code, 200)
        payload = api_data(response)["message"]["structured_payload"]
        all_text = str(payload)
        self.assertEqual(payload["intent"], "makeup_look")
        self.assertIn("底妆", all_text)
        self.assertIn("眉眼", all_text)
        self.assertIn("唇颊", all_text)

    def test_product_match_question_returns_risk_and_order_sections(self):
        client, session_factory = make_client()
        with session_factory() as db:
            user = User(display_name="测试用户", login_type="username")
            db.add(user)
            db.commit()
            db.refresh(user)
            user_id = user.id

        response = client.post(
            "/api/chat/messages",
            headers=auth_headers(user_id),
            json={"message": "烟酰胺精华和酸类产品能不能一起用，会不会闷痘？"},
        )

        self.assertEqual(response.status_code, 200)
        payload = api_data(response)["message"]["structured_payload"]
        title = api_data(response)["session"]["title"]
        headings = [section["heading"] for section in payload["sections"]]
        self.assertEqual(payload["intent"], "product_match")
        self.assertEqual(title, "烟酰胺和酸类搭配")
        self.assertIn("搭配风险", headings)
        self.assertIn("使用顺序", headings)

    def test_sensitive_title_removes_phone_email_and_long_noise(self):
        client, session_factory = make_client()
        with session_factory() as db:
            user = User(display_name="测试用户", login_type="username")
            db.add(user)
            db.commit()
            db.refresh(user)
            user_id = user.id

        response = client.post(
            "/api/chat/messages",
            headers=auth_headers(user_id),
            json={"message": "我的邮箱grace@example.com，手机号13812345678，最近闭口粉刺反复怎么办？"},
        )

        self.assertEqual(response.status_code, 200)
        title = api_data(response)["session"]["title"]
        self.assertNotIn("13812345678", title)
        self.assertNotIn("example", title)
        self.assertLessEqual(len(title), 14)
        with session_factory() as db:
            log = db.query(ChatQuestionLog).one()
            self.assertNotIn("grace@example.com", log.normalized_question)
            self.assertIn("[邮箱]", log.normalized_question)

    def test_follow_up_stays_in_same_session_and_history_replays_in_order(self):
        client, session_factory = make_client()
        with session_factory() as db:
            user = User(display_name="测试用户", login_type="username")
            db.add(user)
            db.commit()
            db.refresh(user)
            user_id = user.id

        first = api_data(client.post(
            "/api/chat/messages",
            headers=auth_headers(user_id),
            json={"message": "我最近脸颊泛红刺痛怎么办？"},
        ))
        session_id = first["session"]["id"]
        second = api_data(client.post(
            "/api/chat/messages",
            headers=auth_headers(user_id),
            json={"session_id": session_id, "message": "那今晚还能刷酸吗？"},
        ))
        history = api_data(client.get(f"/api/chat/sessions/{session_id}", headers=auth_headers(user_id)))

        self.assertEqual(second["session"]["id"], session_id)
        self.assertEqual(history["session"]["title"], "脸颊泛红刺痛怎么办")
        self.assertEqual([message["role"] for message in history["messages"]], ["user", "assistant", "user", "assistant"])
        self.assertEqual(history["messages"][0]["content_text"], "我最近脸颊泛红刺痛怎么办？")
        self.assertEqual(history["messages"][2]["content_text"], "那今晚还能刷酸吗？")


if __name__ == "__main__":
    unittest.main()
