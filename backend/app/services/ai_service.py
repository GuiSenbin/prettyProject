"""AI 问答服务 - OpenAI API + 离线规则引擎双模式"""
import logging
from typing import Optional
from openai import OpenAI
from backend.app.config import get_settings

logger = logging.getLogger(__name__)

settings = get_settings()

# ====== 知识库常量 ======
SKIN_TYPE_MAP = {
    "dry": {"name": "干性", "traits": ["皮肤容易紧绷", "容易起皮", "细纹较明显"],
             "routine": "注重保湿补水，使用滋润型产品，避免过度清洁"},
    "oily": {"name": "油性", "traits": ["T区和脸颊容易出油", "毛孔粗大", "容易长痘"],
              "routine": "控油与保湿并重，定期深层清洁，选择清爽型产品"},
    "combination": {"name": "混合性", "traits": ["T区偏油", "脸颊偏干", "局部毛孔粗大"],
                     "routine": "分区护理，T区控油，脸颊保湿，平衡水油"},
    "normal": {"name": "中性", "traits": ["水油平衡", "皮肤状态稳定", "毛孔细腻"],
                "routine": "维持现状为主，做好日常保湿和防晒"},
    "sensitive": {"name": "敏感性", "traits": ["容易泛红", "刺痛发痒", "对成分敏感"],
                   "routine": "温和护肤，修护屏障为主，避免刺激性成分"},
}

CONCERN_MAP = {
    "acne": "痘痘/痘印", "blackhead": "黑头/白头", "wrinkle": "细纹/抗衰",
    "dullness": "暗沉/提亮", "darkcircle": "黑眼圈", "pore": "毛孔粗大",
    "hydration": "保湿补水", "sensitive": "屏障修护",
}


class BeautyAIService:
    """美妆 AI 服务"""

    def __init__(self, db_session=None):
        self.db = db_session
        self._openai_client = None
        if settings.OPENAI_API_KEY:
            kwargs = {"api_key": settings.OPENAI_API_KEY}
            if settings.OPENAI_BASE_URL:
                kwargs["base_url"] = settings.OPENAI_BASE_URL
            self._openai_client = OpenAI(**kwargs)

    # ========== OpenAI 模式 ==========
    def _build_system_prompt(self, user_summary: Optional[dict] = None) -> str:
        prompt = """你是「智颜」的专业 AI 美妆顾问，名叫小蜜。

## 你的角色
- 专业、温柔、有耐心的美妆顾问
- 回答要实用具体，给出可操作步骤
- 使用简体中文，适当用 emoji 让回答更生动

## 专业知识领域
1. 各类肤质护理（干性、油性、混合性、中性、敏感性）
2. 化妆品推荐（洁面、爽肤水、精华、乳液/面霜、防晒、底妆、唇妆、眼妆、面膜）
3. 化妆技巧与教程（日常妆、约会妆、职场妆等）
4. 护肤流程与科学护肤理念
5. 皮肤问题护理（痘痘、黑头、暗沉、敏感、皱纹等）

## 回答原则
- 先分析用户情况再给出建议
- 推荐产品时说明为什么适合该用户
- 信息不全时主动询问（肤质、脸型等）
- 强调防晒重要性
- 严重问题建议咨询皮肤科医生
- 不要编造不存在的产品或成分"""
        if user_summary:
            parts = [f"用户昵称：{user_summary.get('name', '用户')}"]
            if user_summary.get("skin_type"):
                st = SKIN_TYPE_MAP.get(user_summary["skin_type"], {})
                parts.append(f"肤质：{st.get('name', '')}")
            if user_summary.get("face_shape"):
                parts.append(f"脸型：{user_summary['face_shape']}")
            if user_summary.get("concerns"):
                cs = [CONCERN_MAP.get(c, c) for c in user_summary["concerns"]]
                parts.append(f"护肤关注点：{'、'.join(cs)}")
            if user_summary.get("user_products"):
                parts.append(f"用户已拥有的产品：{'、'.join(user_summary['user_products'])}")
                prompt += """\n\n## 重要设定：优先使用已拥有产品
用户现在已经提供了一份他们手头拥有的护肤/美妆产品列表。当你在为用户定制妆容、提供夜间/日间护肤流步骤设计、或者推荐解决皮肤问题的产品时，**你必须优先从用户已拥有的产品中挑选和进行步骤配对**。仅当用户已有的产品库中没有任何适合该步骤的产品、或者完全不推荐在此时使用时，你才可以顺带向用户建议其他市场上的补充产品。在回答中要提及：使用的是他们已有的某款产品。"""
            
            prompt += "\n\n## 当前用户\n" + "\n".join(f"- {p}" for p in parts)
            prompt += "\n\n请根据以上信息提供个性化建议。"
        return prompt

    def _ask_openai(self, message: str, history: list[dict],
                    user_summary: Optional[dict] = None) -> str | None:
        if not self._openai_client:
            return None
        messages = [{"role": "system", "content": self._build_system_prompt(user_summary)}]
        for msg in history[-6:]:
            messages.append({"role": msg.get("role", "user"), "content": msg.get("content", "")})
        messages.append({"role": "user", "content": message})
        try:
            resp = self._openai_client.chat.completions.create(
                model=settings.AI_MODEL, messages=messages,
                temperature=0.7, max_tokens=1200,
            )
            return resp.choices[0].message.content.strip()
        except Exception as e:
            logger.warning(f"OpenAI 调用失败: {e}")
            return None

    # ========== 离线规则引擎 ==========
    def _fallback(self, message: str, user_summary: Optional[dict] = None) -> str:
        msg = message.lower().strip()
        st = user_summary.get("skin_type", "") if user_summary else None
        fs = user_summary.get("face_shape", "") if user_summary else None

        # 检测内联肤质
        inline_skin = None
        if any(kw in msg for kw in ["干性", "干皮"]):
            inline_skin = "dry"
        elif any(kw in msg for kw in ["油性", "油皮", "大油田"]):
            inline_skin = "oily"
        elif "混合" in msg:
            inline_skin = "combination"
        elif "中性" in msg:
            inline_skin = "normal"
        elif any(kw in msg for kw in ["敏感", "泛红", "刺痛"]):
            inline_skin = "sensitive"

        effective_skin = st or inline_skin
        skin_info = SKIN_TYPE_MAP.get(effective_skin) if effective_skin else None

        # —— 妆容 ——
        if any(kw in msg for kw in ["约会", "淡妆", "化妆", "妆容"]):
            return self._makeup_reply(effective_skin, skin_info, fs, user_summary)

        # —— 护肤 ——
        if any(kw in msg for kw in ["护肤", "routine", "步骤", "流程", "怎么护"]):
            return self._skincare_reply(effective_skin, skin_info,
                                        user_summary.get("concerns", []) if user_summary else [],
                                        user_summary)

        # —— 产品推荐 ——
        if any(kw in msg for kw in ["产品", "推荐", "买什么", "好用"]):
            return self._product_reply(effective_skin, skin_info, user_summary)

        # —— 纯告知肤质 ——
        if inline_skin and not any(kw in msg for kw in
                                    ["防晒", "祛痘", "美白", "抗衰", "卸妆"]):
            return (f"了解到你是 **{skin_info['name']}肌肤**！👌\n\n"
                    f"📌 特点：{'、'.join(skin_info['traits'])}\n"
                    f"📌 护理策略：{skin_info['routine']}\n\n"
                    "你想了解什么呢？我可以帮你：\n"
                    "💄 推荐适合你的妆容\n"
                    "🧴 定制护肤方案\n"
                    "📦 推荐适合的产品\n\n直接告诉我就好~ 😊")

        # —— 特定话题 ——
        if "防晒" in msg:
            return ("☀️ **防晒小课堂**\n\n"
                    "防晒是护肤最重要的一步！\n\n"
                    "• 日常通勤：SPF30+ PA+++ 即可\n"
                    "• 户外活动：SPF50+ PA++++\n"
                    "• 用量：一元硬币大小\n"
                    "• 每2-3小时补涂一次\n"
                    "• 无论阴天、室内都要防晒\n\n"
                    "**防晒不仅是防止晒黑，更是防止光老化！**")
        if any(kw in msg for kw in ["祛痘", "痘痘", "痘印"]):
            return ("🔴 **痘痘护理指南**\n\n"
                    "• 不要用手挤痘痘，容易留印留疤\n"
                    "• 使用含水杨酸/壬二酸的产品\n"
                    "• 注意饮食：少吃高糖高GI食物\n"
                    "• 保持枕头套清洁\n"
                    "• 严重痘痘请咨询皮肤科医生")
        if any(kw in msg for kw in ["美白", "提亮", "变白"]):
            return ("✨ **美白攻略**\n\n"
                    "• 防晒是美白的第一步！\n"
                    "• VC、烟酰胺、熊果苷是有效美白成分\n"
                    "• 多喝水，保证睡眠\n"
                    "• 美白需要坚持，28天一个代谢周期\n\n"
                    "⚠️ 不要使用三无美白产品")
        if any(kw in msg for kw in ["抗衰", "抗老", "皱纹", "细纹"]):
            return ("⏳ **抗衰老指南**\n\n"
                    "• 20+就可以开始抗初老\n"
                    "• 视黄醇/胜肽是抗衰王牌成分\n"
                    "• 防晒是最便宜的抗衰手段\n"
                    "• 保持健康作息和饮食\n"
                    "• 眼霜要用起来")
        if "卸妆" in msg:
            return ("🧹 **正确卸妆步骤**\n\n"
                    "• 眼唇用专门的眼唇卸妆液\n"
                    "• 全脸用卸妆油/卸妆膏\n"
                    "• 充分乳化后清水洗净\n"
                    "• 最后用洗面奶二次清洁\n\n"
                    "⚠️ 卸妆不彻底是很多皮肤问题的根源！")

        # 通用回复
        reply = ""
        if skin_info:
            reply += f"根据你的 **{skin_info['name']}肌肤**，"
        reply += "以下是一些美妆护肤小建议：\n\n"
        reply += "• 防晒是护肤的基石，不管什么肤质都要做好 ☀️\n"
        reply += "• 护肤需要耐心，坚持才能看到效果 ✨\n"
        reply += "• 选择产品要适合自己的肤质 💡\n"
        reply += "• 严重皮肤问题建议咨询专业皮肤科医生 🏥\n\n"
        if not st and not inline_skin:
            reply += "去「个人档案」填写肤质信息，我可以给你更精准的建议哦~ 📋"
        else:
            reply += "还有什么我可以帮你的吗？😊"
        return reply

    def _makeup_reply(self, skin_type, skin_info, face_shape, user_summary=None):
        reply = "💄 **约会淡妆步骤** 💄\n\n"
        if skin_info:
            reply += f"根据你的 **{skin_info['name']}肌肤**，我来为你定制妆容：\n\n"
        else:
            reply += "按照通用方案，你也可以告诉我肤质获取更精准的建议~✨\n\n"

        reply += "**Step 1 — 妆前准备**\n• 温和洁面 → 爽肤水 → 保湿乳 → 防晒\n"
        if skin_type == "dry":
            reply += "💡 干皮建议用保湿妆前乳，底妆更服帖\n"
        elif skin_type == "oily":
            reply += "💡 油皮选控油妆前乳，T区重点控油\n"
        elif skin_type == "sensitive":
            reply += "💡 敏感肌选物理防晒，避免刺激\n"

        reply += "\n**Step 2 — 底妆**\n• 轻薄粉底液/气垫，均匀拍开\n• 遮瑕膏点涂痘印、黑眼圈\n• 散粉定妆\n"

        reply += "\n**Step 3 — 眉眼**\n• 自然眉形，眉粉填充\n• 大地色眼影打底\n• 夹翘睫毛，涂睫毛膏\n"

        reply += "\n**Step 4 — 腮红**\n• 杏色/蜜桃色腮红\n"
        face_tips = {"round": "圆脸：斜扫在颧骨下方，视觉拉长",
                      "square": "方脸：颧骨最高处打圈晕染，柔和线条",
                      "oval": "鹅蛋脸：苹果肌轻扫即可",
                      "heart": "心形脸：横向扫在苹果肌，平衡额头",
                      "diamond": "菱形脸：集中在苹果肌，增加饱满感"}
        if face_shape and face_shape in face_tips:
            reply += f"💡 {face_tips[face_shape]}\n"

        reply += "\n**Step 5 — 唇妆**\n• 豆沙色/蜜桃色唇釉，薄涂渐变\n"
        reply += "\n**Step 6 — 定妆**\n• 定妆喷雾全脸定妆\n"

        products = self._get_products(skin_type)
        owned_products = (user_summary or {}).get("user_products") or []
        if owned_products:
            reply += "\n🧰 **优先使用你已有的产品**\n"
            for name in owned_products[:5]:
                reply += f"• {name}\n"
        if products:
            reply += "\n📦 **推荐产品**\n"
            for p in products[:5]:
                reply += f"• {p.get('icon', '📦')} {p['name']}\n"
        return reply

    def _skincare_reply(self, skin_type, skin_info, concerns, user_summary=None):
        if not skin_info:
            return "🧴 在定制方案前，我需要先了解你的肤质哦！\n\n去「个人档案」填写信息，或者告诉我你的肤质~"
        reply = f"🧴 **{skin_info['name']}肌肤专属方案**\n\n"
        reply += f"📌 特点：{'、'.join(skin_info['traits'])}\n"
        reply += f"📌 核心策略：{skin_info['routine']}\n"

        if concerns:
            advice = {"acne": "痘痘→含水杨酸/壬二酸", "blackhead": "黑头→清洁面膜+水杨酸",
                      "wrinkle": "抗衰→视黄醇/胜肽", "dullness": "提亮→VC/烟酰胺",
                      "darkcircle": "黑眼圈→咖啡因眼霜", "pore": "毛孔→水杨酸+控油",
                      "hydration": "保湿→玻尿酸/神经酰胺", "sensitive": "修护→精简护肤"}
            reply += "\n**🎯 护肤重点**\n"
            for c in concerns:
                if c in advice:
                    reply += f"• {advice[c]}\n"

        reply += "\n**推荐流程**\n🌅 日间：洁面→爽肤水→精华→乳液/面霜→防晒\n"
        reply += "🌙 夜间：卸妆→洁面→爽肤水→精华→面霜\n"

        owned_products = (user_summary or {}).get("user_products") or []
        if owned_products:
            reply += "\n🧰 **先从你的产品库里选**\n"
            reply += "你已经登记了：" + "、".join(owned_products[:6]) + "。建议先把这些产品按洁面、精华、保湿、防晒归位，缺哪一步再补买，避免重复消费。\n"

        products = self._get_products(skin_type)
        if products:
            reply += "\n📦 **为你推荐**\n"
            for p in products[:5]:
                reply += f"• {p.get('icon', '📦')} {p['name']}\n"
        return reply

    def _product_reply(self, skin_type, skin_info, user_summary=None):
        if not skin_info:
            return "想推荐产品，但我需要先了解你的肤质哦！💁\n\n去「个人档案」填写信息，或者告诉我你的肤质~"
        reply = f"根据你的 **{skin_info['name']}肌肤**，推荐以下产品：\n\n"
        owned_products = (user_summary or {}).get("user_products") or []
        if owned_products:
            reply += "🧰 **你已有产品优先**\n"
            reply += "你已经登记了：" + "、".join(owned_products[:6]) + "。\n"
            reply += "如果它们能覆盖当前需求，建议先用好已有产品，再决定是否补买。\n\n"
        products = self._get_products(skin_type)
        cats = {}
        for p in products:
            cat = p.get("category_name", "其他")
            if cat not in cats:
                cats[cat] = []
            if len(cats[cat]) < 2:
                cats[cat].append(p)
        for cat, items in cats.items():
            reply += f"**{cat}**\n"
            for p in items:
                reply += f"  {p.get('icon', '📦')} {p['name']}：{p.get('desc', '')}\n"
            reply += "\n"
        reply += "💡 建议先试用小样或到专柜体验后再入手~"
        return reply

    def _get_products(self, skin_type: str = None) -> list[dict]:
        if not self.db:
            return []
        try:
            from sqlalchemy import select
            from backend.app.models.product import Product
            query = select(Product)
            if skin_type:
                query = query.where(Product.suitable.contains(skin_type))
            return [p.to_dict() for p in self.db.execute(query).scalars().all()]
        except Exception:
            return []

    # ========== 统一入口 ==========
    def chat(self, message: str, history: list[dict] = None,
             user_summary: Optional[dict] = None) -> str:
        if self._openai_client:
            reply = self._ask_openai(message, history or [], user_summary)
            if reply:
                return reply
        return self._fallback(message, user_summary)
