"""AI 问答 API 测试：验证多会话、历史回看、重命名和软删除。"""
import json
import unittest
from unittest.mock import patch
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.api import api_router
from backend.app.core.database import Base
from backend.app.core.deps import get_db
from backend.app.modules.chat.models import ChatQuestionLog
from backend.app.modules.profiles.models import UserProfile
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
    def setUp(self):
        class FakeSemanticDeepSeekClient:
            def is_configured(self):
                return True

            def generate_json(self, messages):
                prompt = str(messages)
                if "intent_classification" in prompt:
                    return self._intent_json(messages)
                return (
                    '{"title":"模型回答","summary":"模型根据语义分类生成回答",'
                    '"sections":[{"type":"insight","heading":"判断","body":"这是模型生成的结构化建议。"}],'
                    '"recommended_products":[],"safety_note":"如不适明显，请咨询专业医生。","follow_up_questions":[]}'
                )

            def _intent_json(self, prompt):
                question = self._question_from_messages(prompt)
                if "转行" in question or "股票" in question or "数学作业" in question or "骑自行车" in question:
                    return (
                        '{"intent":"out_of_scope","subject_type":"unknown","answer_level":"refuse",'
                        '"context_policy":{"use_profile":false,"use_products":false,"reason":"问题不属于护肤彩妆范围"},'
                        '"confidence":"high","title":"其他问题","reason":"语义判断为无关问题"}'
                    )
                if "妈妈" in question:
                    return (
                        '{"intent":"skin_sensitive","subject_type":"other_person","answer_level":"cautious",'
                        '"context_policy":{"use_profile":false,"use_products":false,"reason":"替别人咨询，不套用当前用户档案"},'
                        '"confidence":"medium","title":"泛红刺痛咨询","reason":"语义判断为替别人咨询肤况"}'
                    )
                if "怀孕" in question or "孕期" in question or "备孕" in question:
                    return (
                        '{"intent":"pregnancy_safety","subject_type":"hypothetical","answer_level":"high_risk",'
                        '"context_policy":{"use_profile":false,"use_products":false,"reason":"孕期成分问题按安全优先处理"},'
                        '"confidence":"high","title":"孕期成分安全","reason":"语义判断为孕期高风险成分问题"}'
                    )
                if "淡妆" in question or "气色" in question:
                    return (
                        '{"intent":"makeup_look","subject_type":"self","answer_level":"daily",'
                        '"context_policy":{"use_profile":true,"use_products":true,"reason":"需要结合个人档案和产品库做妆容建议"},'
                        '"confidence":"high","title":"清透淡妆","reason":"语义判断为妆容需求"}'
                    )
                if "烟酰胺" in question or "酸类" in question or "一起用" in question:
                    return (
                        '{"intent":"product_match","subject_type":"self","answer_level":"cautious",'
                        '"context_policy":{"use_profile":true,"use_products":true,"reason":"需要结合产品库判断搭配风险"},'
                        '"confidence":"medium","title":"产品搭配判断","reason":"语义判断为产品搭配问题"}'
                    )
                if "痘" in question or "闭口" in question or "粉刺" in question or "泛红" in question or "刺痛" in question:
                    return (
                        '{"intent":"skin_acne","subject_type":"self","answer_level":"cautious",'
                        '"context_policy":{"use_profile":true,"use_products":true,"reason":"需要结合肤况和产品库分析反复长痘"},'
                        '"confidence":"medium","title":"长痘闭口分析","reason":"语义判断为痘痘肤况问题"}'
                    )
                return (
                    '{"intent":"general","subject_type":"unknown","answer_level":"cautious",'
                    '"context_policy":{"use_profile":false,"use_products":false,"reason":"先按通用问题处理"},'
                    '"confidence":"medium","title":"新对话","reason":"语义判断为一般咨询"}'
                )

            def _question_from_messages(self, messages):
                payload = json.loads(messages[1]["content"])
                return payload["question"]

        self.deepseek_patcher = patch("backend.app.modules.chat.service.DeepSeekClient", return_value=FakeSemanticDeepSeekClient())
        self.deepseek_patcher.start()

    def tearDown(self):
        self.deepseek_patcher.stop()

    def test_chat_service_does_not_use_keyword_intent_router(self):
        from pathlib import Path

        service_source = Path("backend/app/modules/chat/service.py").read_text(encoding="utf-8")

        self.assertNotIn("INTENT_KEYWORDS", service_source)
        self.assertNotIn("OTHER_PERSON_KEYWORDS", service_source)
        self.assertNotIn("HYPOTHETICAL_KEYWORDS", service_source)
        self.assertNotIn("SEVERE_SKIN_KEYWORDS", service_source)
        self.assertNotIn("def _detect_intent", service_source)
        self.assertNotIn("def _detect_subject_type", service_source)

    def test_deepseek_config_is_loaded_from_backend_local_env(self):
        from backend.app.core.config import get_settings

        get_settings.cache_clear()
        settings = get_settings()

        self.assertEqual(settings.DEEPSEEK_BASE_URL, "https://api.deepseek.com")
        self.assertEqual(settings.DEEPSEEK_MODEL, "deepseek-v4-flash")
        self.assertEqual(settings.DEEPSEEK_TIMEOUT_SECONDS, 18)

    def test_prompt_requires_json_and_professional_best_friend_style(self):
        from backend.app.modules.chat.prompting import build_chat_messages

        messages = build_chat_messages(
            question="我今天要画一个淡妆，请你给我推荐",
            rule_payload={
                "intent": "makeup_look",
                "subject_type": "self",
                "answer_level": "daily",
                "context_policy": {"use_profile": True},
            },
            context={"profile": None, "user_products": [], "recent_messages": []},
        )

        self.assertIn("json", messages[0]["content"].lower())
        self.assertIn("专业闺蜜型", messages[0]["content"])
        self.assertIn("高风险", messages[0]["content"])
        self.assertIn("makeup_look", messages[1]["content"])

    def test_deepseek_client_uses_json_output(self):
        calls = {}

        class FakeCompletions:
            def create(self, **kwargs):
                calls.update(kwargs)

                class Message:
                    content = '{"title":"ok","summary":"ok","sections":[],"recommended_products":[],"safety_note":"","follow_up_questions":[]}'

                class Choice:
                    message = Message()

                class Response:
                    choices = [Choice()]

                return Response()

        class FakeChat:
            completions = FakeCompletions()

        class FakeOpenAI:
            chat = FakeChat()

        from backend.app.modules.chat.llm_client import DeepSeekClient

        client = DeepSeekClient(
            config={
                "api_key": "test-key",
                "base_url": "https://api.deepseek.com",
                "model": "deepseek-v4-flash",
                "timeout": 18,
            },
            openai_client=FakeOpenAI(),
        )

        result = client.generate_json([{"role": "user", "content": "hi"}])

        self.assertIn('"title"', result)
        self.assertTrue(client.is_configured())
        self.assertEqual(calls["model"], "deepseek-v4-flash")
        self.assertEqual(calls["response_format"], {"type": "json_object"})
        self.assertEqual(calls["stream"], False)

    def test_model_validator_rejects_high_risk_product_recommendations(self):
        from backend.app.modules.chat.validator import validate_model_payload

        with self.assertRaises(ValueError):
            validate_model_payload(
                '{"title":"建议","summary":"总结","sections":[],"recommended_products":[{"name":"某精华"}],"safety_note":"提醒","follow_up_questions":[]}',
                {
                    "intent": "pregnancy_safety",
                    "subject_type": "self",
                    "answer_level": "high_risk",
                    "context_policy": {"use_profile": True},
                },
            )

    def test_send_message_uses_model_when_deepseek_returns_valid_json(self):
        client, session_factory = make_client()
        with session_factory() as db:
            user = User(display_name="测试用户", login_type="username")
            profile = UserProfile(user=user, skin_type="混合偏干", skin_concerns=["暗沉"])
            db.add_all([user, profile])
            db.commit()
            db.refresh(user)
            user_id = user.id

        class FakeDeepSeekClient:
            def __init__(self):
                self.calls = 0

            def is_configured(self):
                return True

            def generate_json(self, messages):
                self.calls += 1
                if "intent_classification" in str(messages):
                    return (
                        '{"intent":"makeup_look","subject_type":"self","answer_level":"daily",'
                        '"context_policy":{"use_profile":true,"use_products":true,"reason":"需要结合个人档案和产品库"},'
                        '"confidence":"high","title":"模型淡妆建议","reason":"语义判断为淡妆需求"}'
                    )
                return '{"title":"模型淡妆建议","summary":"模型回答","sections":[],"recommended_products":[],"safety_note":"安全提醒","follow_up_questions":["今天是什么场合？"]}'

        fake_client = FakeDeepSeekClient()
        with patch("backend.app.modules.chat.service.DeepSeekClient", return_value=fake_client):
            response = client.post(
                "/api/chat/messages",
                headers=auth_headers(user_id),
                json={"message": "今天面试想画淡妆"},
            )

        payload = api_data(response)["message"]["structured_payload"]
        self.assertEqual(fake_client.calls, 2)
        self.assertEqual(payload["source"], "model")
        self.assertEqual(payload["title"], "模型淡妆建议")
        self.assertEqual(payload["intent"], "makeup_look")
        self.assertTrue(payload["context_used"]["profile"])
        self.assertTrue(payload["context_used"]["products"])

    def test_send_message_uses_model_intent_classification_before_answer(self):
        client, session_factory = make_client()
        with session_factory() as db:
            user = User(display_name="测试用户", login_type="username")
            db.add(user)
            db.commit()
            db.refresh(user)
            user_id = user.id

        class FakeDeepSeekClient:
            def __init__(self):
                self.calls = []

            def is_configured(self):
                return True

            def generate_json(self, messages):
                self.calls.append(messages)
                prompt = str(messages)
                if "intent_classification" in prompt:
                    return (
                        '{"intent":"makeup_look","subject_type":"self","answer_level":"daily",'
                        '"context_policy":{"use_profile":true,"use_products":true,"reason":"需要结合个人档案和产品库做妆容建议"},'
                        '"confidence":"high","title":"清透气色妆","reason":"用户想让自己看起来干净有气色，属于妆容需求"}'
                    )
                return (
                    '{"title":"清透气色妆","summary":"模型按妆容需求回答",'
                    '"sections":[{"type":"steps","heading":"妆容路线","items":["底妆薄一点","唇颊同色系"]}],'
                    '"recommended_products":[],"safety_note":"如皮肤不适先暂停上妆。","follow_up_questions":[]}'
                )

        fake_client = FakeDeepSeekClient()
        with patch("backend.app.modules.chat.service.DeepSeekClient", return_value=fake_client):
            response = client.post(
                "/api/chat/messages",
                headers=auth_headers(user_id),
                json={"message": "明天见人，想让自己看起来干净有气色"},
            )

        self.assertEqual(response.status_code, 200)
        payload = api_data(response)["message"]["structured_payload"]
        self.assertEqual(len(fake_client.calls), 2)
        self.assertEqual(payload["source"], "model")
        self.assertEqual(payload["intent"], "makeup_look")
        self.assertEqual(payload["answer_level"], "daily")
        self.assertEqual(api_data(response)["session"]["title"], "清透气色妆")

    def test_model_intent_redirects_unrelated_questions_without_answer_call(self):
        examples = [
            ("怎么骑自行车？", "运动技能问题"),
            ("我想转行做程序员，你觉得怎么样？", "职业规划问题"),
            ("这只股票现在能买吗？", "投资问题"),
            ("帮我写一篇数学作业论文", "作业论文问题"),
        ]
        for question, title in examples:
            with self.subTest(question=question):
                client, session_factory = make_client()
                with session_factory() as db:
                    user = User(display_name="测试用户", login_type="username")
                    db.add(user)
                    db.commit()
                    db.refresh(user)
                    user_id = user.id

                class FakeDeepSeekClient:
                    def __init__(self):
                        self.calls = 0

                    def is_configured(self):
                        return True

                    def generate_json(self, messages):
                        self.calls += 1
                        prompt = str(messages)
                        if "intent_classification" not in prompt:
                            raise AssertionError("无关问题不应该进入正式回答模型")
                        return (
                            '{"intent":"out_of_scope","subject_type":"unknown","answer_level":"refuse",'
                            '"context_policy":{"use_profile":false,"use_products":false,"reason":"问题不属于护肤彩妆范围"},'
                            f'"confidence":"high","title":"{title}","reason":"用户问题与产品定位无关"}}'
                        )

                fake_client = FakeDeepSeekClient()
                with patch("backend.app.modules.chat.service.DeepSeekClient", return_value=fake_client):
                    response = client.post(
                        "/api/chat/messages",
                        headers=auth_headers(user_id),
                        json={"message": question},
                    )

                self.assertEqual(response.status_code, 200)
                payload = api_data(response)["message"]["structured_payload"]
                self.assertEqual(fake_client.calls, 1)
                self.assertEqual(payload["intent"], "out_of_scope")
                self.assertEqual(payload["answer_level"], "refuse")
                self.assertFalse(payload["context_policy"]["use_profile"])
                self.assertFalse(payload["context_policy"]["use_products"])
                self.assertIn("美妆", payload["summary"])

    def test_send_message_falls_back_to_local_rule_when_model_json_invalid(self):
        client, session_factory = make_client()
        with session_factory() as db:
            user = User(display_name="测试用户", login_type="username")
            db.add(user)
            db.commit()
            db.refresh(user)
            user_id = user.id

        class FakeDeepSeekClient:
            def is_configured(self):
                return True

            def generate_json(self, messages):
                return "not json"

        with patch("backend.app.modules.chat.service.DeepSeekClient", return_value=FakeDeepSeekClient()):
            response = client.post(
                "/api/chat/messages",
                headers=auth_headers(user_id),
                json={"message": "今天面试想画淡妆"},
            )

        payload = api_data(response)["message"]["structured_payload"]
        self.assertEqual(payload["source"], "local_rule")
        self.assertEqual(payload["intent"], "general")

    def test_send_message_falls_back_when_model_payload_has_invalid_types(self):
        client, session_factory = make_client()
        with session_factory() as db:
            user = User(display_name="测试用户", login_type="username")
            db.add(user)
            db.commit()
            db.refresh(user)
            user_id = user.id

        class FakeDeepSeekClient:
            def is_configured(self):
                return True

            def generate_json(self, messages):
                return '{"title":"模型标题","summary":null,"sections":[null],"recommended_products":[],"safety_note":"安全提醒","follow_up_questions":[]}'

        with patch("backend.app.modules.chat.service.DeepSeekClient", return_value=FakeDeepSeekClient()):
            response = client.post(
                "/api/chat/messages",
                headers=auth_headers(user_id),
                json={"message": "今天面试想画淡妆"},
            )

        self.assertEqual(response.status_code, 200)
        payload = api_data(response)["message"]["structured_payload"]
        self.assertEqual(payload["source"], "local_rule")
        self.assertEqual(payload["intent"], "general")

    def test_model_prompt_sanitizes_current_question_and_recent_history(self):
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
            json={"message": "我的邮箱grace@example.com，最近长痘怎么办？"},
        ))
        session_id = first["session"]["id"]

        class FakeDeepSeekClient:
            def is_configured(self):
                return True

            def generate_json(self, messages):
                prompt = str(messages)
                if "13812345678" in prompt or "grace@example.com" in prompt:
                    raise AssertionError("敏感信息不应发送给模型")
                self.prompt = prompt
                return '{"title":"模型淡妆建议","summary":"模型回答","sections":[],"recommended_products":[],"safety_note":"安全提醒","follow_up_questions":[]}'

        with patch("backend.app.modules.chat.service.DeepSeekClient", return_value=FakeDeepSeekClient()):
            response = client.post(
                "/api/chat/messages",
                headers=auth_headers(user_id),
                json={"session_id": session_id, "message": "我手机号13812345678，今天面试想画淡妆"},
            )

        self.assertEqual(response.status_code, 200)
        payload = api_data(response)["message"]["structured_payload"]
        self.assertEqual(payload["source"], "model")

    def test_high_risk_question_uses_classifier_but_skips_answer_model(self):
        client, session_factory = make_client()
        with session_factory() as db:
            user = User(display_name="测试用户", login_type="username")
            db.add(user)
            db.commit()
            db.refresh(user)
            user_id = user.id

        class FakeDeepSeekClient:
            def __init__(self):
                self.calls = 0

            def is_configured(self):
                return True

            def generate_json(self, messages):
                self.calls += 1
                if "intent_classification" not in str(messages):
                    raise AssertionError("高风险问题不应该调用正式回答模型")
                return (
                    '{"intent":"pregnancy_safety","subject_type":"hypothetical","answer_level":"high_risk",'
                    '"context_policy":{"use_profile":false,"use_products":false,"reason":"孕期成分问题按安全优先处理"},'
                    '"confidence":"high","title":"孕期成分安全","reason":"模型语义判断为高风险问题"}'
                )

        fake_client = FakeDeepSeekClient()
        with patch("backend.app.modules.chat.service.DeepSeekClient", return_value=fake_client):
            response = client.post(
                "/api/chat/messages",
                headers=auth_headers(user_id),
                json={"message": "我怀孕了还能用A醇吗？"},
            )

        self.assertEqual(response.status_code, 200)
        payload = api_data(response)["message"]["structured_payload"]
        self.assertEqual(fake_client.calls, 1)
        self.assertEqual(payload["source"], "local_rule")
        self.assertEqual(payload["answer_level"], "high_risk")

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
        self.assertEqual(data["session"]["title"], "长痘闭口分析")
        self.assertEqual(data["session"]["title_edited"], False)
        self.assertEqual(data["message"]["role"], "assistant")
        self.assertEqual(data["user_message"]["role"], "user")
        self.assertEqual(data["message"]["structured_payload"]["source"], "model")
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
        self.assertEqual(data["session"]["title"], "清透淡妆")
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
        self.assertEqual(payload["answer_level"], "refuse")
        self.assertEqual(payload["confidence"], "high")
        self.assertFalse(payload["context_policy"]["use_profile"])
        self.assertFalse(payload["context_policy"]["use_products"])

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
        self.assertIn("替别人咨询", payload["context_policy"]["reason"])

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
        self.assertEqual(payload["answer_level"], "high_risk")
        self.assertEqual(payload["confidence"], "high")
        self.assertFalse(payload["context_policy"]["use_profile"])
        self.assertIn("安全", payload["context_policy"]["reason"])

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
        self.assertEqual(payload["intent"], "makeup_look")
        self.assertEqual(payload["answer_level"], "daily")
        self.assertEqual(payload["confidence"], "high")
        self.assertEqual(payload["source"], "model")
        self.assertTrue(payload["context_policy"]["use_profile"])
        self.assertTrue(payload["context_policy"]["use_products"])

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
        self.assertEqual(payload["intent"], "product_match")
        self.assertEqual(payload["answer_level"], "cautious")
        self.assertEqual(payload["confidence"], "medium")
        self.assertTrue(payload["context_policy"]["use_profile"])
        self.assertTrue(payload["context_policy"]["use_products"])
        self.assertEqual(title, "产品搭配判断")

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
        self.assertEqual(history["session"]["title"], "长痘闭口分析")
        self.assertEqual([message["role"] for message in history["messages"]], ["user", "assistant", "user", "assistant"])
        self.assertEqual(history["messages"][0]["content_text"], "我最近脸颊泛红刺痛怎么办？")
        self.assertEqual(history["messages"][2]["content_text"], "那今晚还能刷酸吗？")

    def test_v2_payload_marks_cautious_acne_and_logs_policy_for_knowledge_base(self):
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
            json={"message": "我最近闭口粉刺反复，还能用酸类吗？"},
        )

        self.assertEqual(response.status_code, 200)
        payload = api_data(response)["message"]["structured_payload"]
        self.assertEqual(payload["answer_level"], "cautious")
        self.assertEqual(payload["confidence"], "medium")
        self.assertTrue(payload["context_policy"]["use_profile"])
        self.assertTrue(payload["context_policy"]["use_products"])
        with session_factory() as db:
            log = db.query(ChatQuestionLog).one()
            self.assertEqual(log.context_used["answer_level"], "cautious")
            self.assertEqual(log.context_used["confidence"], "medium")
            self.assertTrue(log.context_used["context_policy"]["use_profile"])


if __name__ == "__main__":
    unittest.main()
