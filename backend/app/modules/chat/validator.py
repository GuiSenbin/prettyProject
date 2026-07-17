"""AI 问答模型输出校验：保证 DeepSeek 结果符合产品安全边界。"""
import json


REQUIRED_FIELDS = (
    "title",
    "summary",
    "sections",
    "recommended_products",
    "safety_note",
    "follow_up_questions",
)

ALLOWED_INTENTS = {
    "skin_acne",
    "skin_sensitive",
    "routine_today",
    "makeup_look",
    "product_match",
    "pregnancy_safety",
    "out_of_scope",
    "general",
}
ALLOWED_SUBJECT_TYPES = {"self", "other_person", "hypothetical", "unknown"}
ALLOWED_ANSWER_LEVELS = {"daily", "cautious", "high_risk", "refuse"}
ALLOWED_CONFIDENCE = {"high", "medium", "low"}


def validate_intent_payload(raw_text: str, fallback_payload: dict) -> dict:
    try:
        data = json.loads(raw_text)
    except json.JSONDecodeError as exc:
        raise ValueError("模型意图识别返回不是合法 JSON") from exc

    if not isinstance(data, dict):
        raise ValueError("模型意图识别必须返回 JSON 对象")
    for field in ("intent", "subject_type", "answer_level", "context_policy", "confidence", "title"):
        if field not in data:
            raise ValueError(f"模型意图识别缺少字段: {field}")

    intent = _enum_value(data, "intent", ALLOWED_INTENTS, fallback_payload.get("intent", "general"))
    subject_type = _enum_value(data, "subject_type", ALLOWED_SUBJECT_TYPES, fallback_payload.get("subject_type", "unknown"))
    answer_level = _enum_value(data, "answer_level", ALLOWED_ANSWER_LEVELS, fallback_payload.get("answer_level", "cautious"))
    confidence = _enum_value(data, "confidence", ALLOWED_CONFIDENCE, fallback_payload.get("confidence", "medium"))
    policy = _validate_context_policy(data.get("context_policy"), fallback_payload.get("context_policy", {}))
    title = data.get("title")
    if not isinstance(title, str) or not title.strip():
        title = fallback_payload.get("title") or "新对话"

    return {
        "source": "model_intent",
        "intent": intent,
        "subject_type": subject_type,
        "answer_level": answer_level,
        "context_policy": policy,
        "confidence": confidence,
        "title": title.strip()[:14],
        "reason": str(data.get("reason") or "").strip(),
    }


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
    _require_non_empty_string(data, "title")
    _require_non_empty_string(data, "summary")
    if data.get("safety_note") is not None and not isinstance(data["safety_note"], str):
        raise ValueError("safety_note 必须是字符串")
    if not isinstance(data["sections"], list):
        raise ValueError("sections 必须是数组")
    if not isinstance(data["recommended_products"], list):
        raise ValueError("recommended_products 必须是数组")
    if not isinstance(data["follow_up_questions"], list):
        raise ValueError("follow_up_questions 必须是数组")
    data["sections"] = [_validate_section(section) for section in data["sections"]]
    data["follow_up_questions"] = [
        question.strip()
        for question in data["follow_up_questions"]
        if isinstance(question, str) and question.strip()
    ][:3]

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
    data["recommended_products"] = data["recommended_products"][:3]
    return data


def _enum_value(data: dict, field: str, allowed: set[str], fallback: str) -> str:
    value = data.get(field)
    if isinstance(value, str) and value in allowed:
        return value
    return fallback


def _validate_context_policy(policy, fallback_policy: dict) -> dict:
    if not isinstance(policy, dict):
        policy = fallback_policy
    return {
        "use_profile": bool(policy.get("use_profile")),
        "use_products": bool(policy.get("use_products")),
        "reason": str(policy.get("reason") or fallback_policy.get("reason") or "").strip(),
    }


def _require_non_empty_string(data: dict, field: str) -> None:
    if not isinstance(data.get(field), str) or not data[field].strip():
        raise ValueError(f"{field} 必须是非空字符串")


def _validate_section(section: dict) -> dict:
    if not isinstance(section, dict):
        raise ValueError("section 必须是对象")
    _require_non_empty_string(section, "type")
    _require_non_empty_string(section, "heading")
    if "body" in section and section["body"] is not None and not isinstance(section["body"], str):
        raise ValueError("section.body 必须是字符串")
    items = section.get("items")
    if items is None:
        return section
    if not isinstance(items, list):
        raise ValueError("section.items 必须是数组")
    if section["type"] == "questions":
        section["items"] = [_validate_question_item(item) for item in items]
    else:
        section["items"] = [item.strip() for item in items if isinstance(item, str) and item.strip()]
    return section


def _validate_question_item(item: dict) -> dict:
    if not isinstance(item, dict):
        raise ValueError("questions item 必须是对象")
    _require_non_empty_string(item, "strong")
    if "text" in item and item["text"] is not None and not isinstance(item["text"], str):
        raise ValueError("questions item.text 必须是字符串")
    return {
        "strong": item["strong"].strip(),
        "text": (item.get("text") or "").strip(),
    }
