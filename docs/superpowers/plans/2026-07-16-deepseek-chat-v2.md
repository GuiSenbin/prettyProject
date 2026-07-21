# DeepSeek Chat V2 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build a genuinely usable AI chat module that calls DeepSeek, uses the user's profile/product/history context, keeps high-risk answers safe, and saves structured answers for exact history replay.

**Architecture:** Keep the current Chat module as the orchestration layer. Add small focused units for DeepSeek calling, user context assembly, prompt construction, model-output validation, and anonymized logging. Local code remains responsible for intent/risk/context policy; DeepSeek is responsible for natural-language answer generation inside that boundary.

**Tech Stack:** FastAPI, SQLAlchemy, OpenAI-compatible Python SDK, DeepSeek Chat Completions API, Vue 3, Pinia, unittest.

## Global Constraints

- All final user-facing AI responses must fit the product tone: professional best-friend, warm, specific, not salesy, and not fear-inducing.
- Never commit or hard-code API keys. Use `DEEPSEEK_API_KEY` from environment variables only.
- Because a key appeared in chat, rotate it before production or shared-device smoke testing.
- DeepSeek OpenAI-compatible base URL is `https://api.deepseek.com`.
- Default model is `deepseek-v4-flash`; allow override with `DEEPSEEK_MODEL`.
- Use DeepSeek JSON Output with `response_format={"type":"json_object"}`.
- The prompt must contain the word `json` and a concrete JSON example.
- AI must read user data when the question benefits from it: skin profile, user product library, product ingredients, and recent conversation history.
- High-risk questions must not recommend specific products. They may give risk avoidance, stop-use guidance, and doctor/dermatologist prompts.
- Low-risk product-type questions, such as cleanser or simple daily makeup advice, may recommend safe categories or user-owned products when appropriate.
- Off-topic questions should be answered briefly with a warm boundary and redirected to beauty, skincare, makeup, or product-use support.
- Saved history must display saved `structured_payload`; never recall DeepSeek to reconstruct old answers.
- If DeepSeek fails, times out, returns empty content, invalid JSON, or unsafe payload, fallback to local-rule response and persist the fallback source.
- No new table is required for chat sessions/messages because those already exist; add only missing fields/tables if tests prove current schema cannot persist the required data.

---

## Requirement Review

The current Chat module is useful as a scaffold, but it is not a real model-backed feature yet. `backend/app/modules/chat/service.py` currently generates answers from local rules and labels them as `source: "local_rule"`. That means the module cannot yet handle open-ended requests like "今天要画一个淡妆怎么搭" with real language intelligence, nor can it adapt deeply to the user's skin profile and product library.

The correct V2 direction is controlled model integration, not unrestricted model chat. Local code should still decide: what is the user's intent, whether the issue is high-risk, what user context may be used, and whether product recommendation is allowed. DeepSeek then writes the final answer in a strict JSON contract. The validator rejects anything outside the boundary.

## File Structure

- Modify: `backend/app/core/config.py`
  - Expose `DEEPSEEK_API_KEY`, `DEEPSEEK_BASE_URL`, `DEEPSEEK_MODEL`, and timeout settings.
- Create: `backend/app/modules/chat/context_builder.py`
  - Build compact user context from profile, user products, product ingredients, and recent messages.
- Create: `backend/app/modules/chat/prompting.py`
  - Define system prompt, user payload, JSON schema contract, and off-topic/high-risk instructions.
- Create: `backend/app/modules/chat/llm_client.py`
  - Call DeepSeek through OpenAI-compatible SDK and return raw JSON text.
- Create: `backend/app/modules/chat/validator.py`
  - Parse JSON, enforce required fields, repair safe metadata, and reject unsafe product recommendations.
- Modify: `backend/app/modules/chat/service.py`
  - Orchestrate local policy, context building, DeepSeek call, validation, persistence, and fallback.
- Modify: `backend/app/modules/chat/repository.py`
  - Add anonymized Q&A log helper if existing methods do not cover it.
- Modify: `backend/tests/test_chat_api.py`
  - Add model-success, fallback, high-risk, off-topic, context, history-replay, and anonymized-log tests.
- Modify: `frontend/src/views/Chat/index.vue`
  - Display model/fallback source subtly and render structured history without refetching AI.
- Optional Modify: `docs/architecture.md`, `docs/database-guide.md`
  - Document DeepSeek chat flow and source semantics after implementation passes.

---

### Task 1: DeepSeek Configuration

**Files:**
- Modify: `backend/app/core/config.py`
- Test: `backend/tests/test_chat_api.py`

**Interfaces:**
- Produces: `get_settings().DEEPSEEK_API_KEY: str`
- Produces: `get_settings().DEEPSEEK_BASE_URL: str`
- Produces: `get_settings().DEEPSEEK_MODEL: str`
- Produces: `get_settings().DEEPSEEK_TIMEOUT_SECONDS: int`

- [ ] **Step 1: Write the failing test**

Add to `backend/tests/test_chat_api.py`:

```python
class ChatConfigTest(unittest.TestCase):
    def test_deepseek_config_is_environment_driven(self):
        import os
        from backend.app.core.config import get_settings

        get_settings.cache_clear()
        os.environ["DEEPSEEK_API_KEY"] = "test-key"
        os.environ["DEEPSEEK_BASE_URL"] = "https://api.deepseek.com"
        os.environ["DEEPSEEK_MODEL"] = "deepseek-v4-flash"
        os.environ["DEEPSEEK_TIMEOUT_SECONDS"] = "18"

        settings = get_settings()

        self.assertEqual(settings.DEEPSEEK_API_KEY, "test-key")
        self.assertEqual(settings.DEEPSEEK_BASE_URL, "https://api.deepseek.com")
        self.assertEqual(settings.DEEPSEEK_MODEL, "deepseek-v4-flash")
        self.assertEqual(settings.DEEPSEEK_TIMEOUT_SECONDS, 18)
```

- [ ] **Step 2: Run test to verify failure before implementation**

```bash
./.venv/bin/python -m unittest backend.tests.test_chat_api.ChatConfigTest.test_deepseek_config_is_environment_driven
```

Expected before implementation: missing-attribute failure.

- [ ] **Step 3: Implement settings**

In `backend/app/core/config.py`, add:

```python
DEEPSEEK_API_KEY: str = os.getenv("DEEPSEEK_API_KEY", "")
DEEPSEEK_BASE_URL: str = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com")
DEEPSEEK_MODEL: str = os.getenv("DEEPSEEK_MODEL", "deepseek-v4-flash")
DEEPSEEK_TIMEOUT_SECONDS: int = int(os.getenv("DEEPSEEK_TIMEOUT_SECONDS", "18"))
```

- [ ] **Step 4: Run test to verify pass**

```bash
./.venv/bin/python -m unittest backend.tests.test_chat_api.ChatConfigTest.test_deepseek_config_is_environment_driven
```

Expected: `OK`.

- [ ] **Step 5: Commit**

```bash
git add backend/app/core/config.py backend/tests/test_chat_api.py
git commit -m "feat: add DeepSeek chat configuration"
```

---

### Task 2: Chat Context Builder

**Files:**
- Create: `backend/app/modules/chat/context_builder.py`
- Modify: `backend/tests/test_chat_api.py`

**Interfaces:**
- Produces: `ChatContextBuilder(db: Session)`
- Produces: `ChatContextBuilder.build(user_id: str, session=None) -> dict`

- [ ] **Step 1: Write the failing test**

Add to `backend/tests/test_chat_api.py`:

```python
def test_context_builder_includes_profile_products_and_recent_history(self):
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
        json={"message": "我最近长痘怎么办？"},
    ))

    from backend.app.modules.chat.context_builder import ChatContextBuilder
    with session_factory() as db:
        service = ChatService(db)
        session = service.chat.get_session(user_id, first["session"]["id"])
        context = ChatContextBuilder(db).build(user_id, session)

    self.assertIn("profile", context)
    self.assertIn("user_products", context)
    self.assertIn("recent_messages", context)
    self.assertLessEqual(len(context["recent_messages"]), 8)
```

- [ ] **Step 2: Run test to verify failure**

```bash
./.venv/bin/python -m unittest backend.tests.test_chat_api.ChatApiTest.test_context_builder_includes_profile_products_and_recent_history
```

Expected: import error for missing `context_builder`.

- [ ] **Step 3: Implement context builder**

Create `backend/app/modules/chat/context_builder.py`:

```python
"""AI 问答上下文构建：组装用户档案、产品库和最近会话历史。"""
from sqlalchemy.orm import Session

from backend.app.modules.products.repository import ProductRepository
from backend.app.modules.profiles.repository import ProfileRepository


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
            "user_products": [self._product_item(item) for item in user_products[:12]],
            "recent_messages": [
                {
                    "role": message.role,
                    "content": message.content_text,
                    "intent": message.intent,
                    "subject_type": message.subject_type,
                }
                for message in messages[-8:]
            ],
        }

    def _product_item(self, item) -> dict:
        product = item.product
        if not product:
            return {"name": item.display_name(), "source": item.source, "ingredients": []}
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
```

- [ ] **Step 4: Run test to verify pass**

```bash
./.venv/bin/python -m unittest backend.tests.test_chat_api.ChatApiTest.test_context_builder_includes_profile_products_and_recent_history
```

Expected: `OK`.

- [ ] **Step 5: Commit**

```bash
git add backend/app/modules/chat/context_builder.py backend/tests/test_chat_api.py
git commit -m "feat: build chat context from user data"
```

---

### Task 3: Prompt Contract and DeepSeek Client

**Files:**
- Create: `backend/app/modules/chat/prompting.py`
- Create: `backend/app/modules/chat/llm_client.py`
- Modify: `backend/tests/test_chat_api.py`

**Interfaces:**
- Produces: `build_chat_messages(question: str, rule_payload: dict, context: dict) -> list[dict]`
- Produces: `DeepSeekClient.generate_json(messages: list[dict]) -> str`
- Produces: `DeepSeekClient.is_configured() -> bool`

- [ ] **Step 1: Write prompt and client tests**

Add to `backend/tests/test_chat_api.py`:

```python
def test_prompt_requires_json_and_professional_best_friend_style(self):
    from backend.app.modules.chat.prompting import build_chat_messages

    messages = build_chat_messages(
        question="我今天要画一个淡妆，请你给我推荐",
        rule_payload={"intent": "makeup_look", "subject_type": "self", "answer_level": "daily", "context_policy": {"use_profile": True}},
        context={"profile": None, "user_products": [], "recent_messages": []},
    )

    system = messages[0]["content"]
    user = messages[1]["content"]
    self.assertIn("json", system.lower())
    self.assertIn("专业闺蜜型", system)
    self.assertIn("高风险", system)
    self.assertIn("makeup_look", user)


def test_deepseek_client_uses_configured_model_and_json_output(self):
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
        config={"api_key": "test-key", "base_url": "https://api.deepseek.com", "model": "deepseek-v4-flash", "timeout": 18},
        openai_client=FakeOpenAI(),
    )

    result = client.generate_json([{"role": "user", "content": "hi"}])

    self.assertIn('"title"', result)
    self.assertTrue(client.is_configured())
    self.assertEqual(calls["model"], "deepseek-v4-flash")
    self.assertEqual(calls["response_format"], {"type": "json_object"})
    self.assertEqual(calls["stream"], False)
```

- [ ] **Step 2: Run tests to verify failure**

```bash
./.venv/bin/python -m unittest backend.tests.test_chat_api.ChatApiTest.test_prompt_requires_json_and_professional_best_friend_style backend.tests.test_chat_api.ChatApiTest.test_deepseek_client_uses_configured_model_and_json_output
```

Expected: import errors for missing modules.

- [ ] **Step 3: Implement prompt builder**

Create `backend/app/modules/chat/prompting.py`:

```python
"""AI 问答提示词：定义 DeepSeek 结构化输出契约。"""
import json


SYSTEM_PROMPT = """
你是智颜的专属 AI 顾问，风格是专业闺蜜型：温柔、具体、克制，不制造焦虑，不夸大功效，不替代医生。
你必须输出严格 json，不要输出 Markdown，不要输出 json 以外的文字。
必须包含字段：source, intent, subject_type, answer_level, context_policy, confidence, title, summary, sections, recommended_products, safety_note, follow_up_questions。
answer_level 只能是 daily/cautious/high_risk/refuse。
高风险问题不得推荐具体产品，只能给避雷、停用观察、安全提醒、就医或皮肤科咨询建议。
如果用户问转行、投资、学习等无关问题，简短共情后引导回护肤、彩妆、产品使用和变美规划。
如果上下文没有用户档案或产品库，不要声称参考了它们。
"""


def build_chat_messages(question: str, rule_payload: dict, context: dict) -> list[dict]:
    example = {
        "source": "model",
        "intent": rule_payload.get("intent"),
        "subject_type": rule_payload.get("subject_type", "unknown"),
        "answer_level": rule_payload.get("answer_level", "cautious"),
        "context_policy": rule_payload.get("context_policy", {}),
        "confidence": "medium",
        "title": "一句话标题",
        "summary": "一句到两句话的核心建议",
        "sections": [{"type": "insight", "heading": "判断", "body": "具体分析"}],
        "recommended_products": [],
        "safety_note": "必要时咨询专业医生。",
        "follow_up_questions": ["是否需要我按你的产品库继续细化？"],
    }
    payload = {
        "question": question,
        "local_policy": rule_payload,
        "context": context,
        "json_example": example,
    }
    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
    ]
```

- [ ] **Step 4: Implement DeepSeek client**

Create `backend/app/modules/chat/llm_client.py`:

```python
"""DeepSeek 客户端：通过 OpenAI 兼容 SDK 调用模型并请求 JSON 输出。"""
from openai import OpenAI

from backend.app.core.config import get_settings


class DeepSeekClient:
    def __init__(self, config: dict | None = None, openai_client=None):
        settings = get_settings()
        resolved = {
            "api_key": settings.DEEPSEEK_API_KEY,
            "base_url": settings.DEEPSEEK_BASE_URL,
            "model": settings.DEEPSEEK_MODEL,
            "timeout": settings.DEEPSEEK_TIMEOUT_SECONDS,
        }
        if config:
            resolved.update(config)
        self.api_key = resolved["api_key"]
        self.model = resolved["model"]
        self.client = openai_client or OpenAI(
            api_key=resolved["api_key"],
            base_url=resolved["base_url"],
            timeout=resolved["timeout"],
        )

    def is_configured(self) -> bool:
        return bool(self.api_key and self.model)

    def generate_json(self, messages: list[dict]) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            response_format={"type": "json_object"},
            temperature=0.4,
            max_tokens=1400,
            stream=False,
        )
        return response.choices[0].message.content or ""
```

- [ ] **Step 5: Run tests to verify pass**

```bash
./.venv/bin/python -m unittest backend.tests.test_chat_api.ChatApiTest.test_prompt_requires_json_and_professional_best_friend_style backend.tests.test_chat_api.ChatApiTest.test_deepseek_client_uses_configured_model_and_json_output
```

Expected: `OK`.

- [ ] **Step 6: Commit**

```bash
git add backend/app/modules/chat/prompting.py backend/app/modules/chat/llm_client.py backend/tests/test_chat_api.py
git commit -m "feat: add DeepSeek JSON prompt client"
```

---

### Task 4: Model Output Validator

**Files:**
- Create: `backend/app/modules/chat/validator.py`
- Modify: `backend/tests/test_chat_api.py`

**Interfaces:**
- Produces: `validate_model_payload(raw_text: str, rule_payload: dict) -> dict`

- [ ] **Step 1: Write validator tests**

Add to `backend/tests/test_chat_api.py`:

```python
def test_model_validator_accepts_valid_json_and_forces_local_policy(self):
    from backend.app.modules.chat.validator import validate_model_payload

    payload = validate_model_payload(
        '{"title":"建议","summary":"总结","sections":[],"recommended_products":[],"safety_note":"提醒","follow_up_questions":[]}',
        {"intent": "makeup_look", "subject_type": "self", "answer_level": "daily", "context_policy": {"use_profile": True, "use_products": False}},
    )

    self.assertEqual(payload["source"], "model")
    self.assertEqual(payload["intent"], "makeup_look")
    self.assertEqual(payload["answer_level"], "daily")
    self.assertEqual(payload["context_policy"], {"use_profile": True, "use_products": False})


def test_model_validator_rejects_high_risk_product_recommendations(self):
    from backend.app.modules.chat.validator import validate_model_payload

    with self.assertRaises(ValueError):
        validate_model_payload(
            '{"title":"建议","summary":"总结","sections":[],"recommended_products":[{"name":"某精华"}],"safety_note":"提醒","follow_up_questions":[]}',
            {"intent": "pregnancy_safety", "subject_type": "self", "answer_level": "high_risk", "context_policy": {"use_profile": True}},
        )


def test_model_validator_rejects_invalid_json(self):
    from backend.app.modules.chat.validator import validate_model_payload

    with self.assertRaises(ValueError):
        validate_model_payload("not json", {"intent": "unknown", "answer_level": "cautious"})
```

- [ ] **Step 2: Run tests to verify failure**

```bash
./.venv/bin/python -m unittest backend.tests.test_chat_api.ChatApiTest.test_model_validator_accepts_valid_json_and_forces_local_policy backend.tests.test_chat_api.ChatApiTest.test_model_validator_rejects_high_risk_product_recommendations backend.tests.test_chat_api.ChatApiTest.test_model_validator_rejects_invalid_json
```

Expected: import error for missing `validator`.

- [ ] **Step 3: Implement validator**

Create `backend/app/modules/chat/validator.py`:

```python
"""AI 问答模型输出校验：保证 DeepSeek 结果符合产品安全边界。"""
import json


REQUIRED_FIELDS = ("title", "summary", "sections", "recommended_products", "safety_note", "follow_up_questions")


def validate_model_payload(raw_text: str, rule_payload: dict) -> dict:
    try:
        data = json.loads(raw_text)
    except json.JSONDecodeError as exc:
        raise ValueError("模型返回不是合法 JSON") from exc

    if not isinstance(data, dict):
        raise ValueError("模型返回必须是 JSON 对象")
    for field in REQUIRED_FIELDS:
        if field not in data:
            raise ValueError(f"模型返回缺少字段: {field}")
    if not isinstance(data["sections"], list):
        raise ValueError("sections 必须是数组")
    if not isinstance(data["recommended_products"], list):
        raise ValueError("recommended_products 必须是数组")
    if not isinstance(data["follow_up_questions"], list):
        raise ValueError("follow_up_questions 必须是数组")

    answer_level = rule_payload.get("answer_level", "cautious")
    if answer_level == "high_risk" and data["recommended_products"]:
        raise ValueError("高风险问题禁止推荐具体产品")

    data["source"] = "model"
    data["intent"] = rule_payload.get("intent")
    data["subject_type"] = rule_payload.get("subject_type")
    data["answer_level"] = answer_level
    data["context_policy"] = rule_payload.get("context_policy", {})
    data["confidence"] = data.get("confidence") or rule_payload.get("confidence") or "medium"
    data["context_used"] = {
        "profile": bool(data["context_policy"].get("use_profile")),
        "products": bool(data["context_policy"].get("use_products")),
    }
    return data
```

- [ ] **Step 4: Run tests to verify pass**

```bash
./.venv/bin/python -m unittest backend.tests.test_chat_api.ChatApiTest.test_model_validator_accepts_valid_json_and_forces_local_policy backend.tests.test_chat_api.ChatApiTest.test_model_validator_rejects_high_risk_product_recommendations backend.tests.test_chat_api.ChatApiTest.test_model_validator_rejects_invalid_json
```

Expected: `OK`.

- [ ] **Step 5: Commit**

```bash
git add backend/app/modules/chat/validator.py backend/tests/test_chat_api.py
git commit -m "feat: validate model chat payloads"
```

---

### Task 5: Chat Service DeepSeek Orchestration and Fallback

**Files:**
- Modify: `backend/app/modules/chat/service.py`
- Modify: `backend/tests/test_chat_api.py`

**Interfaces:**
- Consumes: `ChatContextBuilder.build(user_id, session)`
- Consumes: `build_chat_messages(question, rule_payload, context)`
- Consumes: `DeepSeekClient.generate_json(messages)`
- Consumes: `validate_model_payload(raw_text, rule_payload)`
- Produces: assistant message with `structured_payload.source == "model"` when model succeeds.
- Produces: assistant message with `structured_payload.source == "local_rule"` when fallback is used.

- [ ] **Step 1: Add dependency-injection seam test for model success**

Add to `backend/tests/test_chat_api.py`:

```python
def test_send_message_uses_model_when_deepseek_returns_valid_json(self):
    client, session_factory = make_client()
    with session_factory() as db:
        user = User(display_name="测试用户", login_type="username")
        db.add(user)
        db.commit()
        db.refresh(user)
        user_id = user.id

    from backend.app.modules.chat import service as chat_service_module
    original_client = chat_service_module.DeepSeekClient

    class FakeDeepSeekClient:
        def is_configured(self):
            return True

        def generate_json(self, messages):
            return '{"title":"模型淡妆建议","summary":"模型回答","sections":[],"recommended_products":[],"safety_note":"安全提醒","follow_up_questions":["今天是什么场合？"]}'

    chat_service_module.DeepSeekClient = lambda: FakeDeepSeekClient()
    try:
        response = client.post(
            "/api/chat/messages",
            headers=auth_headers(user_id),
            json={"message": "今天面试想画淡妆"},
        )
    finally:
        chat_service_module.DeepSeekClient = original_client

    payload = api_data(response)["message"]["structured_payload"]
    self.assertEqual(payload["source"], "model")
    self.assertEqual(payload["title"], "模型淡妆建议")
    self.assertEqual(payload["intent"], "makeup_look")
```

- [ ] **Step 2: Add fallback test**

Add:

```python
def test_send_message_falls_back_to_local_rule_when_model_json_invalid(self):
    client, session_factory = make_client()
    with session_factory() as db:
        user = User(display_name="测试用户", login_type="username")
        db.add(user)
        db.commit()
        db.refresh(user)
        user_id = user.id

    from backend.app.modules.chat import service as chat_service_module
    original_client = chat_service_module.DeepSeekClient

    class FakeDeepSeekClient:
        def is_configured(self):
            return True

        def generate_json(self, messages):
            return "not json"

    chat_service_module.DeepSeekClient = lambda: FakeDeepSeekClient()
    try:
        response = client.post(
            "/api/chat/messages",
            headers=auth_headers(user_id),
            json={"message": "今天面试想画淡妆"},
        )
    finally:
        chat_service_module.DeepSeekClient = original_client

    payload = api_data(response)["message"]["structured_payload"]
    self.assertEqual(payload["source"], "local_rule")
    self.assertEqual(payload["intent"], "makeup_look")
```

- [ ] **Step 3: Run tests to verify failure**

```bash
./.venv/bin/python -m unittest backend.tests.test_chat_api.ChatApiTest.test_send_message_uses_model_when_deepseek_returns_valid_json backend.tests.test_chat_api.ChatApiTest.test_send_message_falls_back_to_local_rule_when_model_json_invalid
```

Expected: first test returns `local_rule`, second may pass only accidentally; orchestration is incomplete.

- [ ] **Step 4: Implement orchestration**

In `backend/app/modules/chat/service.py`, import:

```python
from backend.app.modules.chat.context_builder import ChatContextBuilder
from backend.app.modules.chat.llm_client import DeepSeekClient
from backend.app.modules.chat.prompting import build_chat_messages
from backend.app.modules.chat.validator import validate_model_payload
```

Add helper inside `ChatService`:

```python
    def _build_ai_payload(self, user_id: str, session, content: str, rule_payload: dict) -> dict:
        client = DeepSeekClient()
        if not client.is_configured():
            return rule_payload
        try:
            context = ChatContextBuilder(self.db).build(user_id, session)
            messages = build_chat_messages(content, rule_payload, context)
            raw_text = client.generate_json(messages)
            return validate_model_payload(raw_text, rule_payload)
        except Exception:
            return rule_payload
```

Then in the send-message path, replace direct use of local `structured_payload` for assistant answer with:

```python
rule_payload = self._build_structured_answer(content)
structured_payload = self._build_ai_payload(user_id, session, content, rule_payload)
```

- [ ] **Step 5: Run tests to verify pass**

```bash
./.venv/bin/python -m unittest backend.tests.test_chat_api.ChatApiTest.test_send_message_uses_model_when_deepseek_returns_valid_json backend.tests.test_chat_api.ChatApiTest.test_send_message_falls_back_to_local_rule_when_model_json_invalid
```

Expected: `OK`.

- [ ] **Step 6: Commit**

```bash
git add backend/app/modules/chat/service.py backend/tests/test_chat_api.py
git commit -m "feat: route chat answers through DeepSeek with fallback"
```

---

### Task 6: Safety and Topic Behavior Tests

**Files:**
- Modify: `backend/app/modules/chat/service.py`
- Modify: `backend/tests/test_chat_api.py`

**Interfaces:**
- Produces: local policy with `answer_level == "high_risk"` for sensitive medical/pregnancy/allergy/burning symptoms.
- Produces: local policy with `answer_level == "refuse"` or `intent == "off_topic"` for unrelated life/career/investment questions.

- [ ] **Step 1: Add high-risk and off-topic tests**

Add:

```python
def test_high_risk_question_never_recommends_products_even_if_model_tries(self):
    client, session_factory = make_client()
    with session_factory() as db:
        user = User(display_name="测试用户", login_type="username")
        db.add(user)
        db.commit()
        db.refresh(user)
        user_id = user.id

    from backend.app.modules.chat import service as chat_service_module
    original_client = chat_service_module.DeepSeekClient

    class FakeDeepSeekClient:
        def is_configured(self):
            return True

        def generate_json(self, messages):
            return '{"title":"不安全推荐","summary":"总结","sections":[],"recommended_products":[{"name":"强功效精华"}],"safety_note":"提醒","follow_up_questions":[]}'

    chat_service_module.DeepSeekClient = lambda: FakeDeepSeekClient()
    try:
        response = client.post(
            "/api/chat/messages",
            headers=auth_headers(user_id),
            json={"message": "我怀孕了还能用A醇和酸类吗？"},
        )
    finally:
        chat_service_module.DeepSeekClient = original_client

    payload = api_data(response)["message"]["structured_payload"]
    self.assertEqual(payload["source"], "local_rule")
    self.assertEqual(payload["answer_level"], "high_risk")
    self.assertEqual(payload.get("recommended_products", []), [])


def test_off_topic_question_redirects_without_fake_beauty_advice(self):
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
        json={"message": "我想转行做程序员，你觉得怎么办？"},
    )

    payload = api_data(response)["message"]["structured_payload"]
    self.assertIn(payload["intent"], ["off_topic", "unknown"])
    self.assertIn(payload["answer_level"], ["refuse", "cautious"])
    self.assertEqual(payload.get("recommended_products", []), [])
```

- [ ] **Step 2: Run tests to verify current behavior**

```bash
./.venv/bin/python -m unittest backend.tests.test_chat_api.ChatApiTest.test_high_risk_question_never_recommends_products_even_if_model_tries backend.tests.test_chat_api.ChatApiTest.test_off_topic_question_redirects_without_fake_beauty_advice
```

Expected before policy tuning: at least one assertion may fail if intent/risk detection is too weak.

- [ ] **Step 3: Tune local policy**

In `backend/app/modules/chat/service.py`, update `_detect_intent` and structured answer logic so:

```python
HIGH_RISK_KEYWORDS = ("怀孕", "哺乳", "过敏", "刺痛", "红肿", "烂脸", "皮炎", "湿疹", "激素", "药膏", "A醇", "维A酸")
OFF_TOPIC_KEYWORDS = ("转行", "投资", "股票", "考试", "找工作", "辞职", "编程", "买房")
```

Apply:

```python
if any(word in content for word in HIGH_RISK_KEYWORDS):
    intent = "skin_safety"
    answer_level = "high_risk"
    recommended_products = []
elif any(word in content for word in OFF_TOPIC_KEYWORDS):
    intent = "off_topic"
    answer_level = "refuse"
    recommended_products = []
```

- [ ] **Step 4: Run tests to verify pass**

```bash
./.venv/bin/python -m unittest backend.tests.test_chat_api.ChatApiTest.test_high_risk_question_never_recommends_products_even_if_model_tries backend.tests.test_chat_api.ChatApiTest.test_off_topic_question_redirects_without_fake_beauty_advice
```

Expected: `OK`.

- [ ] **Step 5: Commit**

```bash
git add backend/app/modules/chat/service.py backend/tests/test_chat_api.py
git commit -m "feat: enforce chat safety and topic boundaries"
```

---

### Task 7: History Replay and Anonymized Log

**Files:**
- Modify: `backend/app/modules/chat/repository.py`
- Modify: `backend/app/modules/chat/service.py`
- Modify: `backend/tests/test_chat_api.py`

**Interfaces:**
- Produces: history API returns saved assistant `structured_payload` unchanged.
- Produces: anonymized log record for future FAQ/knowledge-base mining.

- [ ] **Step 1: Add history replay test**

Add:

```python
def test_history_replay_uses_saved_payload_without_model_recall(self):
    client, session_factory = make_client()
    with session_factory() as db:
        user = User(display_name="测试用户", login_type="username")
        db.add(user)
        db.commit()
        db.refresh(user)
        user_id = user.id

    sent = api_data(client.post(
        "/api/chat/messages",
        headers=auth_headers(user_id),
        json={"message": "我今天要画淡妆"},
    ))
    session_id = sent["session"]["id"]
    saved_payload = sent["message"]["structured_payload"]

    history = api_data(client.get(
        f"/api/chat/sessions/{session_id}/messages",
        headers=auth_headers(user_id),
    ))

    assistant_messages = [item for item in history["items"] if item["role"] == "assistant"]
    self.assertEqual(assistant_messages[-1]["structured_payload"], saved_payload)
```

- [ ] **Step 2: Add anonymized-log test**

Add:

```python
def test_chat_message_writes_anonymized_qa_log(self):
    client, session_factory = make_client()
    with session_factory() as db:
        user = User(display_name="桂森滨", phone="18638810905", login_type="username")
        db.add(user)
        db.commit()
        db.refresh(user)
        user_id = user.id

    client.post(
        "/api/chat/messages",
        headers=auth_headers(user_id),
        json={"message": "我想找一个温和洁面"},
    )

    with session_factory() as db:
        from backend.app.modules.chat.models import ChatQaLog
        logs = db.query(ChatQaLog).all()
        self.assertGreaterEqual(len(logs), 1)
        self.assertNotIn("18638810905", logs[-1].question_text)
        self.assertNotIn("桂森滨", logs[-1].question_text)
```

- [ ] **Step 3: Run tests to verify behavior**

```bash
./.venv/bin/python -m unittest backend.tests.test_chat_api.ChatApiTest.test_history_replay_uses_saved_payload_without_model_recall backend.tests.test_chat_api.ChatApiTest.test_chat_message_writes_anonymized_qa_log
```

Expected: history may pass; anonymized log may fail if not currently written.

- [ ] **Step 4: Implement anonymization helper**

In `backend/app/modules/chat/service.py`, add:

```python
def _anonymize_text(text: str, user) -> str:
    value = text or ""
    if getattr(user, "phone", None):
        value = value.replace(user.phone, "[phone]")
    if getattr(user, "display_name", None):
        value = value.replace(user.display_name, "[name]")
    return value
```

When persisting Q&A log, use anonymized question and answer text only. If `ChatQaLog` already exists, reuse it. If it does not exist, create an Alembic migration and model with fields:

```python
id: str
user_id: str | None
session_id: str
question_text: str
answer_summary: str
intent: str | None
subject_type: str | None
source: str | None
created_at: datetime
```

- [ ] **Step 5: Run tests to verify pass**

```bash
./.venv/bin/python -m unittest backend.tests.test_chat_api.ChatApiTest.test_history_replay_uses_saved_payload_without_model_recall backend.tests.test_chat_api.ChatApiTest.test_chat_message_writes_anonymized_qa_log
```

Expected: `OK`.

- [ ] **Step 6: Commit**

```bash
git add backend/app/modules/chat backend/tests/test_chat_api.py
git commit -m "feat: preserve chat history and anonymized qa logs"
```

---

### Task 8: Frontend Chat Source and Empty/Error States

**Files:**
- Modify: `frontend/src/views/Chat/index.vue`

**Interfaces:**
- Consumes: `message.structured_payload.source`
- Produces: subtle source label: `AI 生成`, `本地兜底`, or `安全兜底`.

- [ ] **Step 1: Add source label helper**

In `frontend/src/views/Chat/index.vue`, add:

```js
const sourceLabel = (source) => {
  const labels = {
    model: 'AI 生成',
    local_rule: '本地兜底',
    fallback: '安全兜底'
  }
  return labels[source] || 'AI 建议'
}
```

- [ ] **Step 2: Render source label in assistant meta**

In assistant message template:

```vue
<span v-if="item.structured_payload?.source" class="answer-source">
  {{ sourceLabel(item.structured_payload.source) }}
</span>
```

- [ ] **Step 3: Add styles**

```scss
.answer-source {
  padding: 2px 6px;
  border-radius: 8px;
  background: rgba(255, 255, 255, 0.72);
  color: rgba(67, 82, 102, 0.78);
  border: 1px solid rgba(13, 124, 135, 0.10);
  font-size: 10px;
  font-weight: 700;
}
```

- [ ] **Step 4: Build frontend**

```bash
cd frontend
npm run build
```

Expected: build succeeds with no Vue syntax errors.

- [ ] **Step 5: Commit**

```bash
git add frontend/src/views/Chat/index.vue
git commit -m "feat: show chat answer source"
```

---

### Task 9: Full Verification Matrix

**Files:**
- Modify only if verification uncovers bugs in earlier files.

**Interfaces:**
- Verifies all previous public behavior.

- [ ] **Step 1: Run backend chat tests**

```bash
./.venv/bin/python -m unittest backend.tests.test_chat_api
```

Expected: all tests pass.

- [ ] **Step 2: Run frontend build**

```bash
cd frontend
npm run build
```

Expected: build succeeds.

- [ ] **Step 3: Run real DeepSeek smoke test with rotated key**

Do not put the key in source files. In the shell that starts the backend:

```bash
export DEEPSEEK_API_KEY="rotated_deepseek_key_here"
export DEEPSEEK_MODEL="deepseek-v4-flash"
python3 run.py
```

Then send one authenticated `/api/chat/messages` request for:

```json
{"message":"我今天面试想画一个清透淡妆，可以根据我的肤况和产品库帮我安排吗？"}
```

Expected response:

```json
{
  "structured_payload": {
    "source": "model",
    "intent": "makeup_look"
  }
}
```

If `source` is `local_rule`, inspect backend logs for one of:
- Missing `DEEPSEEK_API_KEY`
- DeepSeek network failure
- Invalid or empty JSON output
- Validator rejected unsafe model content

- [ ] **Step 4: Run manual safety smoke tests**

Send:

```json
{"message":"我怀孕了，还能用A醇吗？"}
```

Expected: `answer_level == "high_risk"` and `recommended_products == []`.

Send:

```json
{"message":"我想转行做程序员怎么办？"}
```

Expected: off-topic redirect, no product recommendation.

Send:

```json
{"message":"给我推荐一个温和洁面"}
```

Expected: low-risk answer can recommend safe cleanser type or suitable product-library item.

- [ ] **Step 5: Commit any verification fixes**

```bash
git status --short
git add backend/app/modules/chat backend/tests/test_chat_api.py frontend/src/views/Chat/index.vue docs/architecture.md docs/database-guide.md
git commit -m "test: verify DeepSeek chat integration"
```

---

## Self-Review Checklist

- [ ] Spec coverage: DeepSeek real call, user context, high-risk boundary, off-topic behavior, history replay, anonymized FAQ log, and frontend source display are all mapped to tasks.
- [ ] Placeholder scan: no implementation step relies on an unspecified function without defining it in an earlier task.
- [ ] Type consistency: `build_chat_messages`, `DeepSeekClient.generate_json`, `ChatContextBuilder.build`, and `validate_model_payload` signatures are consistent across tasks.
- [ ] Constitution alignment: backend work stays inside module boundaries; frontend displays status without exposing technical clutter; sensitive key is env-only.

## Execution Choice

Plan complete and saved to `docs/superpowers/plans/2026-07-16-deepseek-chat-v2.md`.

Two execution options:

1. **Subagent-Driven (recommended)** - dispatch a fresh subagent per task, review between tasks, faster iteration with cleaner checkpoints.
2. **Inline Execution** - execute tasks in this session using executing-plans, batch execution with checkpoints.

Which approach?
