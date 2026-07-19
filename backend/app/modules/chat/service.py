"""AI 问答服务：处理多会话、结构化回答和脱敏日志。"""
import re
from fastapi import HTTPException
from sqlalchemy.orm import Session
from backend.app.core.config import get_settings
from backend.app.modules.chat.context_builder import ChatContextBuilder
from backend.app.modules.chat.llm_client import DeepSeekClient
from backend.app.modules.chat.prompting import build_chat_messages, build_intent_messages
from backend.app.modules.chat.privacy import sanitize_text
from backend.app.modules.chat.repository import ChatRepository
from backend.app.modules.chat.schemas import ChatMessageCreate
from backend.app.modules.chat.validator import validate_intent_payload, validate_model_payload
from backend.app.modules.users.repository import UserRepository


class ChatService:
    def __init__(self, db: Session):
        self.chat = ChatRepository(db)
        self.users = UserRepository(db)

    def list_sessions(self, user_id: str) -> list[dict]:
        self._ensure_user_exists(user_id)
        return [self._serialize_session(item) for item in self.chat.list_sessions(user_id, limit=10)]

    def get_session_detail(self, user_id: str, session_id: int) -> dict:
        self._ensure_user_exists(user_id)
        session = self.chat.get_session(user_id, session_id)
        if not session:
            raise HTTPException(404, "会话不存在")
        return {
            "session": self._serialize_session(session),
            "messages": [self._serialize_message(message) for message in session.messages],
        }

    def rename_session(self, user_id: str, session_id: int, title: str) -> dict:
        self._ensure_user_exists(user_id)
        normalized_title = title.strip()
        if not normalized_title:
            raise HTTPException(400, "请输入会话标题")
        session = self.chat.get_session(user_id, session_id)
        if not session:
            raise HTTPException(404, "会话不存在")
        session = self.chat.update_session_title(session, normalized_title[:40], edited=True)
        return self._serialize_session(session)

    def delete_session(self, user_id: str, session_id: int) -> dict:
        self._ensure_user_exists(user_id)
        session = self.chat.get_session(user_id, session_id)
        if not session:
            raise HTTPException(404, "会话不存在")
        self.chat.soft_delete_session(session)
        return {"deleted": True}

    def send_message(self, user_id: str, payload: ChatMessageCreate) -> dict:
        self._ensure_user_exists(user_id)
        question = payload.message.strip()
        if not question:
            raise HTTPException(400, "请输入问题")

        session = self.chat.get_session(user_id, payload.session_id) if payload.session_id else None
        if payload.session_id and not session:
            raise HTTPException(404, "会话不存在")

        intent_payload = self._resolve_intent_payload(user_id, session, question)
        intent = intent_payload["intent"]
        subject_type = intent_payload["subject_type"]
        if not session:
            session = self.chat.create_session(user_id, self._suggest_title(question, intent, intent_payload.get("title")))

        user_message = self.chat.add_message(session, "user", question, intent=intent, subject_type=subject_type)
        rule_payload = self._build_structured_answer(question, intent_payload)
        answer_payload = self._build_ai_payload(user_id, session, question, rule_payload)
        answer = self.chat.add_message(
            session,
            "assistant",
            answer_payload["summary"],
            structured_payload=answer_payload,
            intent=intent,
            subject_type=subject_type,
        )
        normalized_question = self._normalize_question(question)
        self.chat.add_question_log({
            "user_id": user_id,
            "session_id": session.id,
            "raw_question": normalized_question,
            "normalized_question": normalized_question,
            "intent": intent,
            "subject_type": subject_type,
            "context_used": {
                "answer_level": answer_payload["answer_level"],
                "confidence": answer_payload["confidence"],
                "context_policy": answer_payload["context_policy"],
                "intent_source": intent_payload.get("source"),
                "model_source": answer_payload["source"],
            },
            "answer_title": answer_payload["title"],
            "source": answer_payload["source"],
        })
        self.chat.commit()
        return {
            "session": self._serialize_session(session),
            "user_message": self._serialize_message(user_message),
            "message": self._serialize_message(answer),
        }

    def _ensure_user_exists(self, user_id: str) -> None:
        if not self.users.get(user_id):
            raise HTTPException(404, "用户不存在")

    def _resolve_intent_payload(self, user_id: str, session, question: str) -> dict:
        fallback_payload = self._fallback_intent_payload(question)
        try:
            client = DeepSeekClient()
            if not client.is_configured():
                self._debug_model_io("intent skipped", "DEEPSEEK_API_KEY 未配置，已使用通用安全兜底")
                return fallback_payload
            context = ChatContextBuilder(self.chat.db).build(user_id, session)
            messages = build_intent_messages(sanitize_text(question), context)
            self._debug_model_io("intent prompt", messages)
            raw_intent = client.generate_json(messages)
            self._debug_model_io("intent answer", raw_intent)
            intent_payload = validate_intent_payload(raw_intent, fallback_payload)
            return self._enforce_intent_safety(question, intent_payload)
        except Exception as exc:
            self._debug_model_io("intent fallback", str(exc))
            return fallback_payload

    def _fallback_intent_payload(self, question: str) -> dict:
        intent = "general"
        subject_type = "unknown"
        answer_level = self._answer_level_for_intent(intent)
        context_policy = {
            "use_profile": False,
            "use_products": False,
            "reason": "AI 意图识别暂不可用，先不读取个人档案或产品库。",
        }
        return {
            "source": "model_unavailable_fallback",
            "intent": intent,
            "subject_type": subject_type,
            "answer_level": answer_level,
            "context_policy": context_policy,
            "confidence": self._confidence_for_level(answer_level),
            "title": self._suggest_title(question, intent),
            "reason": "模型意图识别不可用时只返回通用安全兜底，不做伪意图判断。",
        }

    def _enforce_intent_safety(self, question: str, intent_payload: dict) -> dict:
        if intent_payload["answer_level"] == "high_risk":
            policy = dict(intent_payload.get("context_policy") or {})
            policy["use_profile"] = False
            policy["use_products"] = False
            policy["reason"] = policy.get("reason") or "高风险问题不推荐具体产品。"
            intent_payload["context_policy"] = policy
        if intent_payload["intent"] == "out_of_scope":
            intent_payload["answer_level"] = "refuse"
            intent_payload["context_policy"] = {
                "use_profile": False,
                "use_products": False,
                "reason": "问题超出美妆护肤范围，不使用个人档案或产品库。",
            }
        return intent_payload

    def _build_ai_payload(self, user_id: str, session, question: str, rule_payload: dict) -> dict:
        if rule_payload.get("answer_level") in ("high_risk", "refuse"):
            return rule_payload
        try:
            client = DeepSeekClient()
            if not client.is_configured():
                self._debug_model_io("skipped", "DEEPSEEK_API_KEY 未配置，已使用本地安全兜底")
                return rule_payload
            model_rule_payload = self._model_context_payload(rule_payload)
            context = ChatContextBuilder(self.chat.db).build(user_id, session)
            messages = build_chat_messages(sanitize_text(question), model_rule_payload, context)
            self._debug_model_io("prompt", messages)
            raw_answer = client.generate_json(messages)
            self._debug_model_io("answer", raw_answer)
            return validate_model_payload(raw_answer, model_rule_payload)
        except Exception as exc:
            self._debug_model_io("fallback", str(exc))
            return rule_payload

    def _debug_model_io(self, label: str, payload) -> None:
        if not get_settings().CHAT_MODEL_DEBUG:
            return
        print(f"[DeepSeek Chat {label}] {sanitize_text(str(payload))[:2000]}")

    def _model_context_payload(self, rule_payload: dict) -> dict:
        payload = dict(rule_payload)
        policy = dict(payload.get("context_policy") or {})
        payload["context_policy"] = {
            "use_profile": bool(policy.get("use_profile")),
            "use_products": bool(policy.get("use_products")),
            "reason": policy.get("reason") or "本次回答按 AI 意图识别结果选择上下文。",
        }
        payload["context_used"] = {
            "profile": bool(payload["context_policy"].get("use_profile")),
            "products": bool(payload["context_policy"].get("use_products")),
        }
        return payload

    def _suggest_title(self, question: str, intent: str, suggested_title: str | None = None) -> str:
        if suggested_title:
            suggested = self._clean_title(suggested_title)
            if suggested:
                return suggested[:14]
        cleaned = self._normalize_question(question)
        cleaned = re.sub(r"\[(手机号|日期)\]", "", cleaned)
        cleaned = re.sub(r"\[邮箱\]", "", cleaned)
        cleaned = re.sub(r"(手机号|手机号码|电话|日期|邮箱)", "", cleaned)
        cleaned = re.sub(r"[，。！？!?、\s]+", "", cleaned)
        cleaned = re.sub(r"^(我最近|我的|我想|最近|请问|帮我|我)", "", cleaned)
        cleaned = re.sub(r"(一下|特别|需要|怎么处理)$", "", cleaned)
        if intent == "out_of_scope":
            return (cleaned[:10] or "其他问题").strip()
        return (cleaned[:14] or "新对话").strip()

    def _clean_title(self, title: str) -> str:
        cleaned = sanitize_text(title)
        cleaned = re.sub(r"\[(手机号|日期|邮箱)\]", "", cleaned)
        cleaned = re.sub(r"[，。！？!?、\s]+", "", cleaned)
        return cleaned.strip()

    def _normalize_question(self, question: str) -> str:
        return sanitize_text(question)

    def _build_structured_answer(self, question: str, intent_payload: dict) -> dict:
        intent = intent_payload["intent"]
        subject_type = intent_payload["subject_type"]
        title_map = {
            "skin_acne": "先按痘痘波动来观察",
            "skin_sensitive": "先按敏感不稳定来处理",
            "routine_today": "先给你一套今日护理思路",
            "makeup_look": "先走干净自然的妆容路线",
            "product_match": "先看搭配风险和使用顺序",
            "pregnancy_safety": "孕期先按安全优先处理",
            "out_of_scope": "这个问题先不展开",
        }
        title = title_map.get(intent, "我先帮你理清思路")
        summary = self._summary_for_intent(intent)
        answer_level = intent_payload.get("answer_level") or self._answer_level_for_intent(intent)
        context_policy = intent_payload.get("context_policy") or self._context_policy_for(intent, subject_type)
        return {
            "source": "local_rule",
            "intent": intent,
            "subject_type": subject_type,
            "answer_level": answer_level,
            "context_policy": context_policy,
            "confidence": intent_payload.get("confidence") or self._confidence_for_level(answer_level),
            "context_used": {
                "profile": context_policy["use_profile"],
                "products": context_policy["use_products"],
            },
            "title": title,
            "summary": summary,
            "sections": self._sections_for_intent(intent, subject_type),
            "recommended_products": [],
            "safety_note": self._safety_note_for_intent(intent),
            "follow_up_questions": self._follow_up_questions_for_intent(intent),
        }

    def _answer_level_for_intent(self, intent: str) -> str:
        if intent in ("makeup_look", "routine_today"):
            return "daily"
        if intent in ("skin_acne", "skin_sensitive", "product_match", "general"):
            return "cautious"
        if intent == "pregnancy_safety":
            return "high_risk"
        if intent == "out_of_scope":
            return "refuse"
        return "cautious"

    def _confidence_for_level(self, answer_level: str) -> str:
        if answer_level in ("daily", "high_risk", "refuse"):
            return "high"
        return "medium"

    def _context_policy_for(self, intent: str, subject_type: str) -> dict:
        if intent == "out_of_scope":
            return {
                "use_profile": False,
                "use_products": False,
                "reason": "问题超出美妆护肤范围，不使用个人档案或产品库。",
            }
        if intent == "pregnancy_safety":
            return {
                "use_profile": False,
                "use_products": False,
                "reason": "孕期或高风险成分问题按安全优先处理，不给强个性化结论。",
            }
        if subject_type == "other_person":
            return {
                "use_profile": False,
                "use_products": False,
                "reason": "这是替别人咨询，不套用当前用户档案。",
            }
        if intent == "product_match":
            return {
                "use_profile": False,
                "use_products": False,
                "reason": "当前未读取个人档案或产品库，仅按通用成分搭配原则给谨慎建议。",
            }
        return {
            "use_profile": False,
            "use_products": False,
            "reason": "当前未读取个人档案，先按通用美妆护肤原则回答。",
        }

    def _follow_up_questions_for_intent(self, intent: str) -> list[str]:
        if intent == "makeup_look":
            return ["你今天是通勤、约会还是正式场合？", "更想要清透感还是遮瑕力？"]
        if intent == "product_match":
            return ["这两个产品的完整名称或成分表是什么？", "你现在使用频率是一周几次？"]
        if intent in ("skin_acne", "skin_sensitive", "general"):
            return ["这个情况持续多久了？", "最近有没有新增产品或刷酸？"]
        if intent == "pregnancy_safety":
            return ["目前是备孕、孕期还是哺乳期？", "产品成分表里是否明确写了视黄醇或水杨酸？"]
        return []

    def _summary_for_intent(self, intent: str) -> str:
        if intent == "out_of_scope":
            return "这个问题超出了美妆护肤助手的范围，我可以帮你把它转回护肤、妆容或产品选择相关的问题。"
        if intent == "makeup_look":
            return "我先给你一套轻量、清透、不容易出错的妆容安排。"
        if intent == "product_match":
            return "我会先按成分刺激性、叠加风险和使用顺序帮你判断。"
        if intent == "pregnancy_safety":
            return "孕期和备孕期先以安全为第一优先，不建议用高风险活性成分硬扛效果。"
        return "我会先给你一个安全、可执行的方向；更准确的判断还需要结合你的档案和产品库。"

    def _sections_for_intent(self, intent: str, subject_type: str) -> list[dict]:
        if intent == "out_of_scope":
            return [
                {
                    "type": "redirect",
                    "heading": "我能帮你的范围",
                    "body": "我更适合回答护肤、妆容、产品搭配、成分避雷和日常护理问题。",
                },
                {
                    "type": "examples",
                    "heading": "可以这样问我",
                    "items": ["今天面试想画淡妆怎么安排？", "最近长痘应该先停哪些产品？", "这两个产品能不能一起用？"],
                },
            ]
        if intent == "makeup_look":
            return [
                {"type": "steps", "heading": "底妆", "items": ["先薄涂妆前或保湿乳，底妆少量多次铺开。", "瑕疵只局部遮，不把全脸盖厚。"]},
                {"type": "steps", "heading": "眉眼", "items": ["眉毛顺着原生眉形补空缺，眼妆用低饱和大地色。", "面试或通勤场景优先干净，不追求强存在感。"]},
                {"type": "steps", "heading": "唇颊", "items": ["腮红和口红选同色系，先少量叠加。", "整体保持气色好、边界柔和。"]},
            ]
        if intent == "product_match":
            return [
                {"type": "insight", "heading": "搭配风险", "body": "烟酰胺和酸类不是绝对不能同用，但同一晚叠加更容易刺激、泛红或闷痘。"},
                {"type": "steps", "heading": "使用顺序", "items": ["先把酸类安排在低频夜间，烟酰胺放在不刷酸的早晚。", "如果刺痛或爆皮，先停酸类，保湿修护 3-5 天。"]},
                {"type": "questions", "heading": "我还需要确认", "items": [{"strong": "酸类浓度和频率是多少？", "text": "浓度越高、频率越密，越需要分开用。"}]},
            ]
        if intent == "pregnancy_safety":
            return [
                {"type": "insight", "heading": "安全判断", "body": "孕期、备孕和哺乳期建议避开视黄醇、维 A 醇等强功效抗老成分。"},
                {"type": "steps", "heading": "替代思路", "items": ["抗老先转为防晒、保湿、温和抗氧化。", "想用功效精华前，优先确认成分表并咨询医生。"]},
            ]
        return [
            {
                "type": "insight",
                "heading": "初步判断",
                "body": self._intent_intro(intent, subject_type),
            },
            {
                "type": "questions",
                "heading": "我想先确认",
                "items": [
                    {"strong": "目前最明显的表现是什么？", "text": "比如红肿、刺痛、干燥、出油、脱妆或闷痘。"},
                    {"strong": "大概持续多久了？", "text": "是最近几天突然出现，还是已经反复几周。"},
                ],
            },
            {
                "type": "steps",
                "heading": "你现在可以先这样做",
                "items": ["先减少叠加步骤，避免频繁更换产品。", "如果不适明显加重，优先暂停高刺激产品。"],
            },
        ]

    def _safety_note_for_intent(self, intent: str) -> str:
        if intent == "pregnancy_safety":
            return "孕期涉及视黄醇、水杨酸等成分时，建议先暂停并咨询医生或产检医生。"
        if intent == "out_of_scope":
            return "我不会替代职业、法律、医疗等专业决策；可以继续问我美妆护肤相关问题。"
        return "如果出现明显红肿疼痛、脓包增多、破溃或持续加重，建议及时咨询皮肤科医生。"

    def _intent_intro(self, intent: str, subject_type: str) -> str:
        if subject_type == "other_person":
            return "这是替别人咨询，我先不套用你的个人档案，会按通用谨慎原则给建议。"
        if intent == "skin_acne":
            return "长痘常见会和油脂分泌、毛孔堵塞、炎症反应、作息压力或近期产品变化有关。"
        if intent == "makeup_look":
            return "淡妆或通勤妆建议先保证底妆轻薄、气色干净，再根据肤况决定遮瑕和定妆强度。"
        return "我会先按日常美妆护肤场景帮你拆解，避免给出过度绝对的判断。"

    def _serialize_session(self, session) -> dict:
        return {
            "id": session.id,
            "title": session.title,
            "title_edited": bool(session.title_edited),
            "created_at": session.created_at.isoformat() if session.created_at else None,
            "updated_at": session.updated_at.isoformat() if session.updated_at else None,
        }

    def _serialize_message(self, message) -> dict:
        return {
            "id": message.id,
            "role": message.role,
            "content_text": message.content_text,
            "structured_payload": message.structured_payload,
            "intent": message.intent,
            "subject_type": message.subject_type,
            "created_at": message.created_at.isoformat() if message.created_at else None,
        }
