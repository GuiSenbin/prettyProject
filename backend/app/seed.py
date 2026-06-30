"""种子数据 - 初始化产品和达人数据"""
import logging
from sqlalchemy import select
from backend.app.database import SessionLocal, init_db
from backend.app.models.product import Product
from backend.app.models.influencer import Influencer

logger = logging.getLogger(__name__)

PRODUCTS = [
    {"name": "氨基酸温和洁面乳", "icon": "🧼", "category": "cleanser", "category_name": "洁面",
     "desc": "弱酸性配方，温和清洁不紧绷，适合所有肤质",
     "skin_tags": ["干性", "敏感", "混合"], "suitable": ["dry", "sensitive", "combination"]},
    {"name": "控油净痘洁面凝胶", "icon": "🧴", "category": "cleanser", "category_name": "洁面",
     "desc": "含水杨酸，深层清洁，控油祛痘",
     "skin_tags": ["油性", "混合"], "suitable": ["oily", "combination"]},
    {"name": "玫瑰保湿爽肤水", "icon": "🌹", "category": "toner", "category_name": "爽肤水",
     "desc": "大马士革玫瑰精华，舒缓保湿，平衡PH值",
     "skin_tags": ["干性", "中性", "混合"], "suitable": ["dry", "normal", "combination"]},
    {"name": "茶树控油爽肤水", "icon": "🌿", "category": "toner", "category_name": "爽肤水",
     "desc": "茶树精华，收敛毛孔，控制油脂分泌",
     "skin_tags": ["油性", "混合"], "suitable": ["oily", "combination"]},
    {"name": "玻尿酸补水精华", "icon": "💧", "category": "essence", "category_name": "精华",
     "desc": "三重玻尿酸，深层补水锁水",
     "skin_tags": ["干性", "中性", "混合", "敏感"],
     "suitable": ["dry", "normal", "combination", "sensitive"]},
    {"name": "维生素C亮肤精华", "icon": "🍊", "category": "essence", "category_name": "精华",
     "desc": "高浓度VC衍生物，抗氧化提亮，改善暗沉",
     "skin_tags": ["干性", "中性", "混合"], "suitable": ["dry", "normal", "combination"]},
    {"name": "视黄醇抗皱精华", "icon": "✨", "category": "essence", "category_name": "精华",
     "desc": "0.3%视黄醇，淡化细纹，促进胶原再生",
     "skin_tags": ["干性", "中性", "混合"], "suitable": ["dry", "normal", "combination"]},
    {"name": "烟酰胺控油精华", "icon": "💎", "category": "essence", "category_name": "精华",
     "desc": "5%烟酰胺，控油抑痘，修护皮肤屏障",
     "skin_tags": ["油性", "混合", "敏感"], "suitable": ["oily", "combination", "sensitive"]},
    {"name": "修护保湿乳霜", "icon": "🧊", "category": "lotion", "category_name": "乳液/面霜",
     "desc": "神经酰胺配方，修护屏障，持久保湿",
     "skin_tags": ["干性", "敏感", "中性"], "suitable": ["dry", "sensitive", "normal"]},
    {"name": "清爽控油凝露", "icon": "🌊", "category": "lotion", "category_name": "乳液/面霜",
     "desc": "无油配方，清爽保湿，控油哑光",
     "skin_tags": ["油性", "混合"], "suitable": ["oily", "combination"]},
    {"name": "轻透防晒乳 SPF50+", "icon": "☀️", "category": "sunscreen", "category_name": "防晒",
     "desc": "物化结合，清爽不闷痘，PA++++",
     "skin_tags": ["所有肤质"], "suitable": ["dry", "oily", "combination", "normal", "sensitive"]},
    {"name": "润色防晒隔离霜", "icon": "🌈", "category": "sunscreen", "category_name": "防晒",
     "desc": "防晒隔离润色三合一，自然提亮",
     "skin_tags": ["干性", "中性", "混合"], "suitable": ["dry", "normal", "combination"]},
    {"name": "水润持妆粉底液", "icon": "🎨", "category": "foundation", "category_name": "底妆",
     "desc": "轻薄水润，自然遮瑕，奶油肌妆效",
     "skin_tags": ["干性", "中性", "混合"], "suitable": ["dry", "normal", "combination"]},
    {"name": "控油哑光粉底液", "icon": "🖌️", "category": "foundation", "category_name": "底妆",
     "desc": "控油持久，哑光妆效，隐形毛孔",
     "skin_tags": ["油性", "混合"], "suitable": ["oily", "combination"]},
    {"name": "遮瑕膏", "icon": "🔲", "category": "foundation", "category_name": "底妆",
     "desc": "高遮盖力，自然服帖，痘印黑眼圈一网打尽",
     "skin_tags": ["所有肤质"], "suitable": ["dry", "oily", "combination", "normal", "sensitive"]},
    {"name": "水光气垫粉底", "icon": "💫", "category": "foundation", "category_name": "底妆",
     "desc": "随身补妆神器，水光妆效",
     "skin_tags": ["干性", "中性", "混合"], "suitable": ["dry", "normal", "combination"]},
    {"name": "丝绒哑光唇釉", "icon": "💋", "category": "lip", "category_name": "唇妆",
     "desc": "丝绒质地，持久不脱色",
     "skin_tags": ["所有肤质"], "suitable": ["dry", "oily", "combination", "normal", "sensitive"]},
    {"name": "润唇膏", "icon": "💄", "category": "lip", "category_name": "唇妆",
     "desc": "天然植物油脂，深层滋润，淡化唇纹",
     "skin_tags": ["干性", "敏感"], "suitable": ["dry", "sensitive"]},
    {"name": "四色眼影盘", "icon": "🎨", "category": "eye", "category_name": "眼妆",
     "desc": "大地色系，百搭日常，粉质细腻显色",
     "skin_tags": ["所有肤质"], "suitable": ["dry", "oily", "combination", "normal", "sensitive"]},
    {"name": "防水眼线笔", "icon": "✏️", "category": "eye", "category_name": "眼妆",
     "desc": "极细笔芯，流畅顺滑，防晕染",
     "skin_tags": ["所有肤质"], "suitable": ["dry", "oily", "combination", "normal", "sensitive"]},
    {"name": "纤长卷翘睫毛膏", "icon": "🪄", "category": "eye", "category_name": "眼妆",
     "desc": "纤长卷翘，持久定型",
     "skin_tags": ["所有肤质"], "suitable": ["dry", "oily", "combination", "normal", "sensitive"]},
    {"name": "补水面膜", "icon": "💦", "category": "mask", "category_name": "面膜",
     "desc": "玻尿酸+积雪草，密集补水舒缓",
     "skin_tags": ["干性", "敏感", "中性"], "suitable": ["dry", "sensitive", "normal"]},
    {"name": "清洁泥膜", "icon": "🧹", "category": "mask", "category_name": "面膜",
     "desc": "高岭土+活性炭，深层清洁，吸附油脂黑头",
     "skin_tags": ["油性", "混合"], "suitable": ["oily", "combination"]},
    {"name": "修护舒缓面膜", "icon": "🌱", "category": "mask", "category_name": "面膜",
     "desc": "泛醇+神经酰胺，修护屏障，舒缓泛红",
     "skin_tags": ["敏感", "干性"], "suitable": ["sensitive", "dry"]},
]

INFLUENCERS = [
    {"name": "小鹿的化妆台", "tag": "妆容教程", "category": "makeup",
     "banner": "💄", "avatar": "🦌", "title": "专业化妆师 | 10年经验",
     "content": "圆脸女生必学的修容大法！通过高光和阴影的搭配，轻松打造小V脸。推荐使用深一色号的粉底做侧影，配合高光提亮T区和下巴。",
     "products": ["修容粉", "高光", "粉底液"],
     "bg": "linear-gradient(135deg, #b8e6d4, #e8f5ee)"},
    {"name": "成分护肤说", "tag": "护肤心得", "category": "skincare",
     "banner": "🧪", "avatar": "🔬", "title": "护肤品成分研究员",
     "content": "油皮夏日护肤三大原则：适度清洁、精简护肤、防晒到位。不要过度追求清爽而忽略保湿，选对成分比选贵更重要。",
     "products": ["水杨酸洁面", "烟酰胺精华", "清爽防晒"],
     "bg": "linear-gradient(135deg, #d0ebe0, #f0faf5)"},
    {"name": "彩妆种草机", "tag": "产品测评", "category": "review",
     "banner": "🌟", "avatar": "🎀", "title": "资深美妆博主",
     "content": "近期最爱——玻尿酸气垫粉底真实测评！水光感十足，遮瑕力中等，适合干皮和混干皮。持妆6小时后T区微微出油，整体妆效依然在线。",
     "products": ["玻尿酸气垫", "定妆喷雾", "妆前乳"],
     "bg": "linear-gradient(135deg, #c8e6d5, #e0f2e8)"},
    {"name": "敏感肌日记", "tag": "护肤心得", "category": "skincare",
     "banner": "🌿", "avatar": "🍃", "title": "敏感肌护理达人",
     "content": "敏感肌换季必看！护肤做减法——温和洁面+保湿精华+修护面霜三步即可。避免酒精、香精、高浓度酸类成分。",
     "products": ["氨基酸洁面", "修护精华", "屏障修护霜"],
     "bg": "linear-gradient(135deg, #b0e0cf, #e0f5ea)"},
    {"name": "裸妆教主", "tag": "妆容教程", "category": "makeup",
     "banner": "✨", "avatar": "👩", "title": "日常妆容设计师",
     "content": "5分钟通勤裸妆教程：隔离+轻薄粉底+眉粉+豆沙色唇釉+腮红。重点在于底妆要透，眼妆要淡，突出好气色。",
     "products": ["润色隔离", "轻薄粉底", "豆沙色唇釉", "腮红"],
     "bg": "linear-gradient(135deg, #d5ede2, #f5fcf8)"},
    {"name": "抗衰护肤指南", "tag": "护肤心得", "category": "skincare",
     "banner": "⏳", "avatar": "🧴", "title": "皮肤科医生",
     "content": "25+抗初老护肤攻略：日间抗氧(VC)+防晒，夜间修护(视黄醇/胜肽)+保湿。眼霜要用起来，眼部是最容易暴露年龄的地方。",
     "products": ["VC精华", "视黄醇精华", "眼霜", "防晒霜"],
     "bg": "linear-gradient(135deg, #c0e4d4, #e8f5ee)"},
]


def seed_database():
    """初始化种子数据"""
    init_db()
    db = SessionLocal()
    try:
        if not db.execute(select(Product).limit(1)).scalar_one_or_none():
            for p in PRODUCTS:
                db.add(Product(**p))
            db.commit()
            logger.info(f"✅ 导入 {len(PRODUCTS)} 个产品")
        if not db.execute(select(Influencer).limit(1)).scalar_one_or_none():
            for i in INFLUENCERS:
                db.add(Influencer(**i))
            db.commit()
            logger.info(f"✅ 导入 {len(INFLUENCERS)} 位达人")
    finally:
        db.close()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    seed_database()
    print("种子数据初始化完成！")
