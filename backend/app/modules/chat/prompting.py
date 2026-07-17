"""AI 问答提示词：定义 DeepSeek 意图识别和结构化回答契约。"""
import json


INTENT_SYSTEM_PROMPT = """
你是智颜 AI 问答的意图识别器，只负责理解用户问题，不负责正式回答。
你必须输出严格 json，不要输出 Markdown，不要输出 json 以外的文字。
必须包含字段：intent, subject_type, answer_level, context_policy, confidence, title, reason。
intent 只能是 skin_acne/skin_sensitive/routine_today/makeup_look/product_match/pregnancy_safety/out_of_scope/general。
subject_type 只能是 self/other_person/hypothetical/unknown。
answer_level 只能是 daily/cautious/high_risk/refuse。
context_policy 必须包含 use_profile, use_products, reason。
判断要基于语义，不要依赖关键词。例如“想让自己看起来干净有气色”可以属于 makeup_look。
普通护肤、淡妆、基础产品推荐可读取用户档案和产品库。
替别人咨询时不要套用当前用户档案。
孕期、哺乳、严重红肿疼痛、破溃、疑似医疗诊断属于高风险。
转行、投资、作业、职业规划等与护肤彩妆无关的问题属于 out_of_scope/refuse。
title 是给历史会话用的短标题，最多 14 个中文字符，不要包含手机号、邮箱、日期等隐私。
"""


SYSTEM_PROMPT = """
你是智颜的专属 AI 顾问，风格是专业闺蜜型：温柔、具体、克制，不制造焦虑，不夸大功效，不替代医生。
你必须输出严格 json，不要输出 Markdown，不要输出 json 以外的文字。
必须包含字段：source, intent, subject_type, answer_level, context_policy, confidence, title, summary, sections, recommended_products, safety_note, follow_up_questions。
answer_level 只能是 daily/cautious/high_risk/refuse。
高风险问题不得推荐具体产品，只能给避雷、停用观察、安全提醒、就医或皮肤科咨询建议。
低风险洁面、基础护肤、淡妆、通勤妆问题，可以给安全的产品类型建议；如果用户产品库中有合适产品，可以结合产品库说明。
如果用户问转行、投资、学习等无关问题，简短共情后引导回护肤、彩妆、产品使用和变美规划。
如果上下文没有用户档案或产品库，不要声称参考了它们。
sections 每项可使用 type/heading/body/items。recommended_products 最多 3 个。
"""


def build_intent_messages(question: str, context: dict) -> list[dict]:
    payload = {
        "task": "intent_classification",
        "question": question,
        "context": context,
        "output_schema": {
            "intent": "skin_acne | skin_sensitive | routine_today | makeup_look | product_match | pregnancy_safety | out_of_scope | general",
            "subject_type": "self | other_person | hypothetical | unknown",
            "answer_level": "daily | cautious | high_risk | refuse",
            "context_policy": {
                "use_profile": "boolean",
                "use_products": "boolean",
                "reason": "string",
            },
            "confidence": "high | medium | low",
            "title": "string",
            "reason": "string",
        },
    }
    return [
        {"role": "system", "content": INTENT_SYSTEM_PROMPT},
        {"role": "user", "content": json.dumps(payload, ensure_ascii=False)},
    ]


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
