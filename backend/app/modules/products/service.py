"""产品模块服务：处理产品搜索、个人产品库和轻量成分匹配分析。"""
from fastapi import HTTPException
from sqlalchemy.orm import Session
from backend.app.modules.products.models import Product, UserProduct
from backend.app.modules.products.repository import ProductRepository
from backend.app.modules.products.schemas import UserProductCreate
from backend.app.modules.profiles.repository import ProfileRepository
from backend.app.modules.users.repository import UserRepository


def _ingredient(inci_name, zh_name, aliases=None, tags=None, description=""):
    return {
        "inci_name": inci_name,
        "zh_name": zh_name,
        "aliases": aliases or [],
        "tags": tags or [],
        "description": description,
    }


SEED_INGREDIENTS = [
    _ingredient("AQUA", "水", ["Water", "Eau"], ["base"], "常见溶剂和配方基底。"),
    _ingredient("GLYCERIN", "甘油", ["丙三醇"], ["moisturizing"], "常见保湿剂。"),
    _ingredient("ALCOHOL DENAT.", "变性乙醇", ["Alcohol", "乙醇", "酒精", "Alcohol Denat."], ["alcohol", "irritant"], "挥发性溶剂，位置靠前时敏感肌和屏障受损人群应谨慎。"),
    _ingredient("FRAGRANCE", "香精", ["Parfum", "香料"], ["fragrance", "allergen", "irritant"], "香味来源，敏感肌或香精不耐受人群应留意。"),
    _ingredient("NIACINAMIDE", "烟酰胺", ["维生素B3"], ["brightening", "barrier"], "常见提亮和屏障护理成分，不等同于保证美白效果。"),
    _ingredient("SODIUM HYALURONATE", "透明质酸钠", ["玻尿酸"], ["moisturizing"], "常见保湿成分。"),
    _ingredient("SALICYLIC ACID", "水杨酸", ["BHA"], ["acid", "acne_care", "irritant"], "常见角质调理成分，敏感肌需关注浓度和频率。"),
    _ingredient("RETINOL", "视黄醇", ["维A醇"], ["retinoid", "anti_aging", "irritant"], "常见维A类成分，敏感肌、孕哺状态需谨慎。"),
    _ingredient("TRANEXAMIC ACID", "传明酸", ["凝血酸"], ["brightening"], "常见提亮淡斑方向成分，不等同于保证美白效果。"),
    _ingredient("ETHYLHEXYL METHOXYCINNAMATE", "甲氧基肉桂酸乙基己酯", ["Octinoxate"], ["uv_filter"], "常见有机防晒剂。"),
    _ingredient("CETEARYL ALCOHOL", "鲸蜡硬脂醇", ["Cetearyl Alcohol"], ["fatty_alcohol", "emollient"], "脂肪醇类润肤和增稠成分，不按酒精刺激标签处理。"),
    _ingredient("PEG-40 STEARATE", "PEG-40 硬脂酸酯", [], ["emulsifier"], "常见乳化剂。"),
    _ingredient("STEARYL ALCOHOL", "硬脂醇", [], ["fatty_alcohol", "emollient"], "脂肪醇类润肤和增稠成分。"),
    _ingredient("POTASSIUM PHOSPHATE", "磷酸钾", [], ["ph_adjuster"], "常见 pH 调节相关成分。"),
    _ingredient("CERAMIDE NP", "神经酰胺 NP", ["Ceramide 3"], ["barrier"], "常见屏障护理脂质。"),
    _ingredient("CERAMIDE AP", "神经酰胺 AP", [], ["barrier"], "常见屏障护理脂质。"),
    _ingredient("CERAMIDE EOP", "神经酰胺 EOP", [], ["barrier"], "常见屏障护理脂质。"),
    _ingredient("CARBOMER", "卡波姆", [], ["thickener"], "常见增稠和凝胶骨架成分。"),
    _ingredient("GLYCERYL STEARATE", "硬脂酸甘油酯", [], ["emollient", "emulsifier"], "常见润肤和乳化成分。"),
    _ingredient("BEHENTRIMONIUM METHOSULFATE", "山嵛基三甲基铵甲基硫酸盐", [], ["conditioning"], "常见调理成分。"),
    _ingredient("SODIUM LAUROYL LACTYLATE", "月桂酰乳酰乳酸钠", [], ["surfactant", "emulsifier"], "常见表面活性和乳化相关成分。"),
    _ingredient("CHOLESTEROL", "胆甾醇", ["Cholesterol"], ["barrier", "emollient"], "皮脂膜相关脂质，常用于屏障护理。"),
    _ingredient("PHENOXYETHANOL", "苯氧乙醇", [], ["preservative"], "常见防腐剂。"),
    _ingredient("DISODIUM EDTA", "EDTA 二钠", [], ["chelating"], "常见螯合剂。"),
    _ingredient("DIPOTASSIUM PHOSPHATE", "磷酸氢二钾", [], ["ph_adjuster"], "常见 pH 调节相关成分。"),
    _ingredient("ASCORBIC ACID", "抗坏血酸", ["L-Ascorbic Acid", "维生素C"], ["brightening", "antioxidant", "acid"], "纯维生素 C 方向抗氧化和提亮成分，敏感肌需关注浓度和耐受。"),
    _ingredient("TOCOPHEROL", "生育酚", ["Vitamin E"], ["antioxidant"], "维生素 E 方向抗氧化成分。"),
    _ingredient("FERULIC ACID", "阿魏酸", [], ["antioxidant", "brightening"], "常见抗氧化辅助成分。"),
    _ingredient("PANTHENOL", "泛醇", ["维生素B5"], ["moisturizing", "soothing"], "常见保湿和舒缓成分。"),
    _ingredient("LAURETH-23", "月桂醇聚醚-23", [], ["emulsifier", "surfactant"], "常见乳化和表面活性相关成分。"),
    _ingredient("PHYTOSPHINGOSINE", "植物鞘氨醇", [], ["barrier"], "屏障脂质相关成分。"),
    _ingredient("XANTHAN GUM", "黄原胶", [], ["thickener"], "常见增稠成分。"),
    _ingredient("CETYL ALCOHOL", "鲸蜡醇", [], ["fatty_alcohol", "emollient"], "脂肪醇类润肤和增稠成分。"),
    _ingredient("POLYSORBATE 20", "聚山梨醇酯-20", [], ["solubilizer"], "常见增溶剂。"),
    _ingredient("ETHYLHEXYLGLYCERIN", "乙基己基甘油", [], ["preservative_booster", "moisturizing"], "常见防腐辅助和保湿成分。"),
    _ingredient("PENTYLENE GLYCOL", "戊二醇", [], ["moisturizing", "solvent"], "常见保湿和溶剂成分。"),
    _ingredient("ZINC PCA", "吡咯烷酮羧酸锌", [], ["sebum_control", "acne_care"], "常见控油方向成分。"),
    _ingredient("DIMETHYL ISOSORBIDE", "二甲基异山梨醇", [], ["solvent"], "常见溶剂和促渗辅助成分。"),
    _ingredient("TAMARINDUS INDICA SEED GUM", "罗望子籽胶", [], ["thickener"], "常见增稠和成膜相关成分。"),
    _ingredient("ISOCETETH-20", "异鲸蜡醇聚醚-20", [], ["emulsifier", "solubilizer"], "常见乳化和增溶成分。"),
    _ingredient("ETHOXYDIGLYCOL", "乙氧基二甘醇", [], ["solvent"], "常见溶剂。"),
    _ingredient("CHLORPHENESIN", "氯苯甘醚", [], ["preservative", "irritant"], "常见防腐剂，敏感肌需留意耐受。"),
    _ingredient("SQUALANE", "角鲨烷", [], ["moisturizing", "emollient"], "常见润肤脂质。"),
    _ingredient("DIMETHICONE", "聚二甲基硅氧烷", ["Dimethicone"], ["silicone", "skin_protecting"], "常见硅类肤感和保护成分。"),
    _ingredient("ZEA MAYS STARCH", "玉米淀粉", ["Corn Starch"], ["absorbent"], "常见吸附和肤感调节成分。"),
    _ingredient("AMMONIUM POLYACRYLOYLDIMETHYL TAURATE", "聚丙烯酰基二甲基牛磺酸铵", [], ["thickener"], "常见增稠成分。"),
    _ingredient("MYRISTYL MYRISTATE", "肉豆蔻酸肉豆蔻酯", [], ["emollient", "comedogenic", "heavy_oil"], "较厚重润肤酯，痘痘/闭口人群可谨慎观察。"),
    _ingredient("STEARIC ACID", "硬脂酸", [], ["fatty_acid", "emollient"], "常见脂肪酸和乳化结构成分。"),
    _ingredient("POTASSIUM CETYL PHOSPHATE", "鲸蜡醇磷酸酯钾", [], ["emulsifier"], "常见乳化剂。"),
    _ingredient("GLYCERYL STEARATE SE", "自乳化硬脂酸甘油酯", [], ["emollient", "emulsifier"], "常见润肤和乳化成分。"),
    _ingredient("SODIUM HYDROXIDE", "氢氧化钠", [], ["ph_adjuster"], "常见 pH 调节剂。"),
    _ingredient("MYRISTIC ACID", "肉豆蔻酸", [], ["fatty_acid", "comedogenic"], "常见脂肪酸，痘痘/闭口人群可谨慎观察。"),
    _ingredient("PALMITIC ACID", "棕榈酸", [], ["fatty_acid"], "常见脂肪酸。"),
    _ingredient("CAPRYLOYL GLYCINE", "辛酰甘氨酸", [], ["skin_conditioning"], "常见皮肤调理成分。"),
    _ingredient("CAPRYLYL GLYCOL", "辛甘醇", [], ["moisturizing", "preservative_booster"], "常见保湿和防腐辅助成分。"),
    _ingredient("STYRENE/ACRYLATES COPOLYMER", "苯乙烯/丙烯酸酯类共聚物", [], ["film_forming"], "常见成膜成分。"),
    _ingredient("POLYMETHYLSILSESQUIOXANE", "聚甲基倍半硅氧烷", [], ["silicone", "texture"], "常见肤感修饰成分。"),
    _ingredient("BUTYLOCTYL SALICYLATE", "水杨酸丁辛酯", [], ["emollient", "solvent"], "常见防晒配方润肤和溶剂成分。"),
    _ingredient("POLY C10-30 ALKYL ACRYLATE", "C10-30 烷基丙烯酸酯聚合物", [], ["film_forming"], "常见成膜成分。"),
    _ingredient("CAPRYLYL METHICONE", "辛基聚甲基硅氧烷", [], ["silicone", "emollient"], "常见硅类润肤成分。"),
    _ingredient("TRISILOXANE", "三硅氧烷", [], ["silicone"], "常见挥发性硅类肤感成分。"),
    _ingredient("ACRYLATES/DIMETHICONE COPOLYMER", "丙烯酸酯/聚二甲基硅氧烷共聚物", [], ["film_forming", "silicone"], "常见成膜成分。"),
    _ingredient("DIETHYLHEXYL SYRINGYLIDENEMALONATE", "亚丁香基丙二酸二乙基己酯", [], ["antioxidant"], "常见抗氧化辅助成分。"),
    _ingredient("PEG-100 STEARATE", "PEG-100 硬脂酸酯", [], ["emulsifier"], "常见乳化剂。"),
    _ingredient("PROPYLENE GLYCOL", "丙二醇", [], ["moisturizing", "solvent"], "常见保湿和溶剂成分。"),
    _ingredient("PEG-8 LAURATE", "PEG-8 月桂酸酯", [], ["emulsifier"], "常见乳化剂。"),
    _ingredient("ACRYLATES/C10-30 ALKYL ACRYLATE CROSSPOLYMER", "丙烯酸酯/C10-30 烷基丙烯酸酯交联聚合物", [], ["thickener"], "常见增稠成分。"),
    _ingredient("TRIETHANOLAMINE", "三乙醇胺", [], ["ph_adjuster"], "常见 pH 调节相关成分。"),
    _ingredient("INULIN LAURYL CARBAMATE", "菊粉月桂基氨基甲酸酯", [], ["emulsifier", "thickener"], "常见乳化和增稠辅助成分。"),
    _ingredient("P-ANISIC ACID", "对茴香酸", [], ["preservative_booster"], "常见防腐辅助成分。"),
    _ingredient("CAPRYLIC/CAPRIC TRIGLYCERIDE", "辛酸/癸酸甘油三酯", [], ["emollient"], "常见润肤油脂。"),
    _ingredient("CASSIA ALATA LEAF EXTRACT", "翅荚决明叶提取物", [], ["botanical", "antioxidant"], "植物来源皮肤调理成分。"),
    _ingredient("MALTODEXTRIN", "麦芽糊精", [], ["carrier"], "常见载体和稳定成分。"),
    _ingredient("SODIUM DODECYLBENZENESULFONATE", "十二烷基苯磺酸钠", [], ["surfactant"], "表面活性剂。"),
    _ingredient("AVOBENZONE", "阿伏苯宗", [], ["uv_filter"], "常见 UVA 有机防晒剂。"),
    _ingredient("HOMOSALATE", "胡莫柳酯", [], ["uv_filter"], "常见 UVB 有机防晒剂。"),
    _ingredient("OCTISALATE", "水杨酸乙基己酯", [], ["uv_filter"], "常见 UVB 有机防晒剂。"),
    _ingredient("OCTOCRYLENE", "奥克立林", [], ["uv_filter"], "常见有机防晒剂。"),
    _ingredient("PROPANEDIOL", "丙二醇", ["1,3-Propanediol"], ["moisturizing", "solvent"], "常见保湿和溶剂成分。"),
    _ingredient("ARGININE", "精氨酸", [], ["amino_acid", "moisturizing"], "氨基酸类保湿相关成分。"),
    _ingredient("ASPARTIC ACID", "天冬氨酸", [], ["amino_acid", "moisturizing"], "氨基酸类保湿相关成分。"),
    _ingredient("GLYCINE", "甘氨酸", [], ["amino_acid", "moisturizing"], "氨基酸类保湿相关成分。"),
    _ingredient("ALANINE", "丙氨酸", [], ["amino_acid", "moisturizing"], "氨基酸类保湿相关成分。"),
    _ingredient("SERINE", "丝氨酸", [], ["amino_acid", "moisturizing"], "氨基酸类保湿相关成分。"),
    _ingredient("VALINE", "缬氨酸", [], ["amino_acid", "moisturizing"], "氨基酸类保湿相关成分。"),
    _ingredient("ISOLEUCINE", "异亮氨酸", [], ["amino_acid", "moisturizing"], "氨基酸类保湿相关成分。"),
    _ingredient("PROLINE", "脯氨酸", [], ["amino_acid", "moisturizing"], "氨基酸类保湿相关成分。"),
    _ingredient("THREONINE", "苏氨酸", [], ["amino_acid", "moisturizing"], "氨基酸类保湿相关成分。"),
    _ingredient("HISTIDINE", "组氨酸", [], ["amino_acid", "moisturizing"], "氨基酸类保湿相关成分。"),
    _ingredient("PHENYLALANINE", "苯丙氨酸", [], ["amino_acid", "moisturizing"], "氨基酸类保湿相关成分。"),
    _ingredient("GLUCOSE", "葡萄糖", [], ["humectant"], "常见保湿相关糖类。"),
    _ingredient("MALTOSE", "麦芽糖", [], ["humectant"], "常见保湿相关糖类。"),
    _ingredient("FRUCTOSE", "果糖", [], ["humectant"], "常见保湿相关糖类。"),
    _ingredient("TREHALOSE", "海藻糖", [], ["humectant"], "常见保湿相关糖类。"),
    _ingredient("SODIUM PCA", "PCA 钠", [], ["moisturizing"], "天然保湿因子相关成分。"),
    _ingredient("PCA", "吡咯烷酮羧酸", [], ["moisturizing"], "天然保湿因子相关成分。"),
    _ingredient("SODIUM LACTATE", "乳酸钠", [], ["moisturizing"], "天然保湿因子相关成分。"),
    _ingredient("UREA", "尿素", [], ["moisturizing"], "常见保湿成分。"),
    _ingredient("ALLANTOIN", "尿囊素", [], ["soothing"], "常见舒缓成分。"),
    _ingredient("LINOLEIC ACID", "亚油酸", [], ["fatty_acid", "barrier"], "常见脂肪酸。"),
    _ingredient("OLEIC ACID", "油酸", [], ["fatty_acid", "emollient"], "常见脂肪酸。"),
    _ingredient("PHYTOSTERYL CANOLA GLYCERIDES", "植物甾醇菜籽油甘油酯类", ["Phytosteryl Canola Glycerides"], ["emollient", "barrier"], "常见润肤脂质。"),
    _ingredient("LECITHIN", "卵磷脂", [], ["emollient", "barrier"], "常见脂质和乳化相关成分。"),
    _ingredient("TRIOLEIN", "三油精", [], ["emollient"], "常见润肤油脂。"),
    _ingredient("POLYSORBATE 60", "聚山梨醇酯-60", [], ["emulsifier"], "常见乳化剂。"),
    _ingredient("SODIUM CHLORIDE", "氯化钠", [], ["viscosity"], "常见黏度调节成分。"),
    _ingredient("CITRIC ACID", "柠檬酸", [], ["ph_adjuster", "acid"], "常见 pH 调节剂。"),
    _ingredient("TRISODIUM ETHYLENEDIAMINE DISUCCINATE", "乙二胺二琥珀酸三钠", [], ["chelating"], "常见螯合剂。"),
    _ingredient("SIMMONDSIA CHINENSIS (JOJOBA) SEED OIL", "霍霍巴籽油", ["Jojoba Seed Oil"], ["emollient"], "常见润肤油脂。"),
    _ingredient("SOLANUM LYCOPERSICUM (TOMATO) FRUIT EXTRACT", "番茄果提取物", [], ["botanical", "antioxidant"], "植物来源皮肤调理成分。"),
    _ingredient("ROSMARINUS OFFICINALIS (ROSEMARY) LEAF EXTRACT", "迷迭香叶提取物", [], ["botanical", "antioxidant"], "植物来源抗氧化相关成分。"),
    _ingredient("HYDROXYMETHOXYPHENYL DECANONE", "羟基甲氧基苯基癸酮", [], ["antioxidant"], "常见抗氧化相关成分。"),
    _ingredient("BHT", "丁羟甲苯", [], ["antioxidant"], "常见抗氧化剂。"),
]


BRAND_ORIGIN_COUNTRIES = {
    "阿玛尼": "意大利",
    "安热沙": "日本",
    "Bobbi Brown": "美国",
    "宝拉珍选": "美国",
    "CeraVe": "美国",
    "Charlotte Tilbury": "英国",
    "CPB肌肤之钥": "日本",
    "Dior": "法国",
    "EltaMD": "美国",
    "eltaMD": "美国",
    "IPSA": "日本",
    "La Roche-Posay": "法国",
    "MAC": "加拿大",
    "NARS": "法国",
    "SK-II": "日本",
    "SUQQU": "日本",
    "The Ordinary": "加拿大",
    "Tom Ford": "美国",
    "Urban Decay": "美国",
    "YSL圣罗兰": "法国",
    "芙丽芳丝": "日本",
    "法尔曼": "瑞士",
    "菲洛嘉": "法国",
    "馥蕾诗": "美国",
    "海蓝之谜": "美国",
    "赫莲娜": "澳大利亚",
    "纪梵希": "法国",
    "嘉娜宝": "日本",
    "娇兰": "法国",
    "娇韵诗": "法国",
    "科颜氏": "美国",
    "兰蔻": "法国",
    "理肤泉": "法国",
    "欧莱雅": "法国",
    "倩碧": "美国",
    "适乐肤": "美国",
    "完美日记": "中国",
    "香奈儿": "法国",
    "香缇卡": "美国",
    "修丽可": "美国",
    "雅诗兰黛": "美国",
    "优色林": "德国",
    "资生堂": "日本",
    "至本": "中国",
    "自然哲理": "美国",
    "蒂佳婷": "韩国",
    "黛珂": "日本",
    "薇诺娜": "中国",
    "植村秀": "日本",
}


def _brand_origin_country(brand: str | None) -> str | None:
    return BRAND_ORIGIN_COUNTRIES.get(brand or "")


def _official_product(brand, name, category, source_url, ingredients, image_url=None):
    return {
        "product": {
            "brand": brand,
            "name": name,
            "category": category,
            "image_url": image_url,
            "registration_number": None,
            "brand_origin_country": _brand_origin_country(brand),
            "status": "verified",
            "source": "brand-official",
            "ingredient_source": "品牌官网公开成分表",
            "source_url": source_url,
        },
        "ingredients": ingredients,
    }


SEED_PRODUCTS = [
    _official_product(
        "CeraVe",
        "CeraVe 适乐肤 Hydrating Facial Cleanser",
        "洁面",
        "https://www.cerave.com/skincare/cleansers/hydrating-facial-cleanser",
        [
            "AQUA", "GLYCERIN", "CETEARYL ALCOHOL", "PEG-40 STEARATE", "STEARYL ALCOHOL",
            "POTASSIUM PHOSPHATE", "CERAMIDE NP", "CERAMIDE AP", "CERAMIDE EOP", "CARBOMER",
            "GLYCERYL STEARATE", "BEHENTRIMONIUM METHOSULFATE", "SODIUM LAUROYL LACTYLATE",
            "SODIUM HYALURONATE", "CHOLESTEROL", "PHENOXYETHANOL", "DISODIUM EDTA",
            "DIPOTASSIUM PHOSPHATE", "TOCOPHEROL", "PHYTOSPHINGOSINE", "XANTHAN GUM",
            "CETYL ALCOHOL", "POLYSORBATE 20", "ETHYLHEXYLGLYCERIN",
        ],
    ),
    _official_product(
        "The Ordinary",
        "The Ordinary Niacinamide 10% + Zinc 1%",
        "精华",
        "https://theordinary.com/en-us/niacinamide-10-zinc-1-serum-100436.html",
        [
            "AQUA", "NIACINAMIDE", "PENTYLENE GLYCOL", "ZINC PCA", "DIMETHYL ISOSORBIDE",
            "TAMARINDUS INDICA SEED GUM", "XANTHAN GUM", "ISOCETETH-20", "ETHOXYDIGLYCOL",
            "PHENOXYETHANOL", "CHLORPHENESIN",
        ],
    ),
    _official_product(
        "La Roche-Posay",
        "La Roche-Posay 理肤泉 Toleriane Double Repair Face Moisturizer",
        "乳液/面霜",
        "https://www.laroche-posay.us/our-products/face/face-moisturizer/toleriane-double-repair-face-moisturizer-3337875545792.html",
        [
            "AQUA", "GLYCERIN", "SQUALANE", "DIMETHICONE", "ZEA MAYS STARCH", "NIACINAMIDE",
            "AMMONIUM POLYACRYLOYLDIMETHYL TAURATE", "MYRISTYL MYRISTATE", "STEARIC ACID",
            "CERAMIDE NP", "POTASSIUM CETYL PHOSPHATE", "GLYCERYL STEARATE SE", "SODIUM HYDROXIDE",
            "MYRISTIC ACID", "PALMITIC ACID", "CAPRYLOYL GLYCINE", "CAPRYLYL GLYCOL", "XANTHAN GUM",
        ],
    ),
    _official_product(
        "La Roche-Posay",
        "La Roche-Posay 理肤泉 Anthelios Melt-In Milk SPF 60",
        "防晒",
        "https://www.laroche-posay.us/our-products/sun/body-sunscreen/anthelios-melt-in-milk-sunscreen-spf-60-antheliosmeltinmilk.html",
        [
            "AQUA", "STYRENE/ACRYLATES COPOLYMER", "DIMETHICONE", "POLYMETHYLSILSESQUIOXANE",
            "BUTYLOCTYL SALICYLATE", "GLYCERIN", "ALCOHOL DENAT.", "POLY C10-30 ALKYL ACRYLATE",
            "CAPRYLYL METHICONE", "TRISILOXANE", "ACRYLATES/DIMETHICONE COPOLYMER",
            "DIETHYLHEXYL SYRINGYLIDENEMALONATE", "PEG-100 STEARATE", "GLYCERYL STEARATE",
            "PHENOXYETHANOL", "POTASSIUM CETYL PHOSPHATE", "PROPYLENE GLYCOL", "CAPRYLYL GLYCOL",
            "PEG-8 LAURATE", "ACRYLATES/C10-30 ALKYL ACRYLATE CROSSPOLYMER", "TRIETHANOLAMINE",
            "TOCOPHEROL", "INULIN LAURYL CARBAMATE", "DISODIUM EDTA", "P-ANISIC ACID",
            "CAPRYLIC/CAPRIC TRIGLYCERIDE", "XANTHAN GUM", "CASSIA ALATA LEAF EXTRACT",
            "MALTODEXTRIN", "SODIUM DODECYLBENZENESULFONATE", "AVOBENZONE", "HOMOSALATE",
            "OCTISALATE", "OCTOCRYLENE",
        ],
    ),
    _official_product(
        "The Ordinary",
        "The Ordinary Natural Moisturizing Factors + HA",
        "乳液/面霜",
        "https://theordinary.com/en-us/natural-moisturizing-factors-ha-moisturizer-100435.html",
        [
            "AQUA", "CAPRYLIC/CAPRIC TRIGLYCERIDE", "CETYL ALCOHOL", "PROPANEDIOL", "STEARYL ALCOHOL",
            "GLYCERIN", "SODIUM HYALURONATE", "ARGININE", "ASPARTIC ACID", "GLYCINE", "ALANINE",
            "SERINE", "VALINE", "ISOLEUCINE", "PROLINE", "THREONINE", "HISTIDINE", "PHENYLALANINE",
            "GLUCOSE", "MALTOSE", "FRUCTOSE", "TREHALOSE", "SODIUM PCA", "PCA", "SODIUM LACTATE",
            "UREA", "ALLANTOIN", "LINOLEIC ACID", "OLEIC ACID", "PHYTOSTERYL CANOLA GLYCERIDES",
            "PALMITIC ACID", "STEARIC ACID", "LECITHIN", "TRIOLEIN", "TOCOPHEROL", "CARBOMER",
            "ISOCETETH-20", "POLYSORBATE 60", "SODIUM CHLORIDE", "CITRIC ACID",
            "TRISODIUM ETHYLENEDIAMINE DISUCCINATE", "PENTYLENE GLYCOL", "TRIETHANOLAMINE",
            "SODIUM HYDROXIDE", "PHENOXYETHANOL", "CHLORPHENESIN",
        ],
    ),
    _official_product(
        "The Ordinary",
        "The Ordinary Retinol 0.2% in Squalane",
        "精华",
        "https://theordinary.com/en-us/retinol-02-in-squalane-serum-100439.html",
        [
            "SQUALANE", "CAPRYLIC/CAPRIC TRIGLYCERIDE", "SIMMONDSIA CHINENSIS (JOJOBA) SEED OIL",
            "RETINOL", "SOLANUM LYCOPERSICUM (TOMATO) FRUIT EXTRACT",
            "ROSMARINUS OFFICINALIS (ROSEMARY) LEAF EXTRACT", "HYDROXYMETHOXYPHENYL DECANONE", "BHT",
        ],
    ),
    _official_product(
        "修丽可",
        "修丽可 CE 复合修护精华液",
        "精华",
        "https://www.skinceuticals.com.au/skincare/facial-serums/c-e-ferulic-vitamin-c-serum/SKC_0001.html",
        [
            "AQUA", "ETHOXYDIGLYCOL", "ASCORBIC ACID", "PROPYLENE GLYCOL", "GLYCERIN",
            "LAURETH-23", "TOCOPHEROL", "TRIETHANOLAMINE", "FERULIC ACID", "PANTHENOL",
            "PHENOXYETHANOL", "SODIUM HYALURONATE",
        ],
        "https://www.skinceuticals.com.au/dw/image/v2/BFZM_PRD/on/demandware.static/-/Sites-skinceuticals-master-catalog/default/dwd14c38e1/Products/635494263008/635494363210_C-E-Ferulic-30ml_SkinCeuticals.jpg?q=70&sfrm=jpg&sw=250",
    ),
    {
        "product": {
            "brand": "薇诺娜",
            "name": "薇诺娜 舒敏保湿特护霜",
            "category": "乳液/面霜",
            "registration_number": None,
            "brand_origin_country": _brand_origin_country("薇诺娜"),
            "status": "pending",
            "source": "seed-candidate",
            "ingredient_source": "待用户补充包装成分表",
            "source_url": None,
        },
        "ingredients": [],
    },
]


BENEFIT_GROUPS = [
    ("保湿", {"moisturizing", "humectant", "保湿"}),
    ("舒缓", {"soothing", "舒缓", "抗炎"}),
    ("修护", {"barrier", "skin_protecting", "修护", "屏障修护"}),
    ("抗氧化", {"antioxidant", "抗氧化"}),
    ("美白/提亮", {"brightening", "美白", "提亮"}),
    ("防晒", {"uv_filter", "防晒"}),
    ("抗老", {"anti_aging", "retinoid", "抗老", "抗皱"}),
    ("控油/祛痘", {"sebum_control", "acne_care", "控油", "祛痘"}),
]

BENEFIT_DISPLAY_PRIORITY = {
    "修护": 10,
    "抗氧化": 20,
    "美白/提亮": 30,
    "抗老": 40,
    "控油/祛痘": 50,
    "舒缓": 60,
    "防晒": 70,
    "保湿": 90,
}

SAFETY_GROUPS = [
    ("香精", {"fragrance"}),
    ("酒精", {"alcohol"}),
    ("酸类/高活性", {"acid", "retinoid"}),
    ("防腐剂", {"preservative", "preservative_booster"}),
    ("致痘关注", {"comedogenic", "heavy_oil"}),
    ("孕哺慎用", {"retinoid"}),
]


class ProductService:
    def __init__(self, db: Session):
        self.products = ProductRepository(db)
        self.users = UserRepository(db)
        self.profiles = ProfileRepository(db)

    def list_my_products(self, user_id: str) -> list[dict]:
        self._ensure_user_exists(user_id)
        self._ensure_seed_data()
        return [self._serialize_user_product(item, user_id) for item in self.products.list_user_products(user_id)]

    def search_products(self, query: str = "", page: int = 1, size: int = 12) -> list[dict]:
        self._ensure_seed_data()
        skip = (page - 1) * size
        products = self.products.search(query, skip=skip, limit=size)
        return [self._serialize_product_summary(p) for p in products]

    def add_my_product(self, user_id: str, payload: UserProductCreate) -> dict:
        self._ensure_user_exists(user_id)
        self._ensure_seed_data()
        if payload.product_id is not None:
            product = self.products.get_product(payload.product_id)
            if not product:
                raise HTTPException(404, "产品不存在")
            item = self.products.create_user_product({
                "user_id": user_id,
                "product_id": product.id,
                "status": "active",
                "source": "master",
            })
            return self._serialize_user_product(item, user_id)

        item = self.products.create_user_product({
            "user_id": user_id,
            "custom_name": payload.name.strip() if payload.name else "待完善产品",
            "status": "pending",
            "source": "manual",
        })
        return self._serialize_user_product(item, user_id)

    def delete_my_product(self, user_id: str, user_product_id: int) -> None:
        self._ensure_user_exists(user_id)
        item = self.products.get_user_product(user_id, user_product_id)
        if not item:
            raise HTTPException(404, "产品库记录不存在")
        self.products.delete_user_product(item)

    def analyze(self, product_id: int, user_id: str | None = None) -> dict:
        self._ensure_seed_data()
        product = self.products.get_product(product_id)
        if not product:
            raise HTTPException(404, "产品不存在")
        profile = self.profiles.get_by_user_id(user_id) if user_id else None
        return self._analyze_product(product, profile.to_dict() if profile else None)

    def get_detail(self, product_id: int, user_id: str | None = None) -> dict:
        self._ensure_seed_data()
        product = self.products.get_product(product_id)
        if not product:
            raise HTTPException(404, "产品不存在")
        profile = self.profiles.get_by_user_id(user_id) if user_id else None
        safety_groups = self._ingredient_groups(product, SAFETY_GROUPS)
        risk_tags = [group["name"] for group in safety_groups if group["count"]]
        if not product.ingredients:
            safety_summary = "缺少完整成分表，无法生成安全提示"
        elif risk_tags:
            safety_summary = f"含有需留意成分：{'、'.join(risk_tags)}"
        else:
            safety_summary = "未标记高关注成分"
        return {
            "product": self._serialize_product_summary(product),
            "analysis": self._analyze_product(product, profile.to_dict() if profile else None),
            "benefit_groups": self._ingredient_groups(product, BENEFIT_GROUPS),
            "safety_groups": safety_groups,
            "safety_summary": safety_summary,
        }

    def _ensure_user_exists(self, user_id: str) -> None:
        if not self.users.get(user_id):
            raise HTTPException(404, "用户不存在")

    def _ensure_seed_data(self) -> None:
        if self.products.has_products():
            return
        ingredients_by_inci = {}
        for payload in SEED_INGREDIENTS:
            ingredient = self.products.get_ingredient_by_inci(payload["inci_name"])
            if not ingredient:
                ingredient = self.products.create_ingredient(payload)
            ingredients_by_inci[payload["inci_name"]] = ingredient

        for item in SEED_PRODUCTS:
            product = self.products.create_product(item["product"])
            for position, inci_name in enumerate(item["ingredients"], start=1):
                ingredient = ingredients_by_inci.get(inci_name)
                if ingredient:
                    self.products.attach_ingredient(product, ingredient, position)
        self.products.commit()


    def _serialize_user_product(self, item: UserProduct, user_id: str) -> dict:
        product_summary = self._serialize_product_summary(item.product) if item.product else None
        analysis = (
            self.analyze(item.product_id, user_id)
            if item.product_id
            else self._incomplete_analysis()
        )
        return {
            "id": item.id,
            "status": item.status,
            "source": item.source,
            "custom_name": item.custom_name,
            "product": product_summary,
            "analysis": analysis,
            "created_at": item.created_at.isoformat() if item.created_at else None,
        }

    def _serialize_product_summary(self, product: Product) -> dict:
        summary = product.to_summary()
        summary["ingredient_count"] = len(product.ingredients or [])
        summary["benefit_tags"] = self._display_benefit_tags(product)
        summary["risk_tags"] = [group["name"] for group in self._ingredient_groups(product, SAFETY_GROUPS) if group["count"]]
        return summary

    def _display_benefit_tags(self, product: Product) -> list[str]:
        tags = [group["name"] for group in self._ingredient_groups(product, BENEFIT_GROUPS) if group["count"]]
        category = product.category or ""
        if category in {"精华", "水乳面霜", "乳液/面霜"} and len(tags) > 1:
            tags = [tag for tag in tags if tag != "保湿"]
        if tags == ["保湿"]:
            return []
        return sorted(tags, key=lambda tag: BENEFIT_DISPLAY_PRIORITY.get(tag, 999))[:2]

    def _ingredient_groups(self, product: Product, groups: list[tuple[str, set[str]]]) -> list[dict]:
        result = []
        for name, matched_tags in groups:
            ingredients = []
            for item in product.ingredients or []:
                ingredient = item.ingredient
                if not ingredient:
                    continue
                traits = set(ingredient.tags or []) | set(getattr(ingredient, "purposes", None) or [])
                if traits.intersection(matched_tags):
                    ingredients.append(ingredient.to_dict(item.position))
            result.append({
                "name": name,
                "count": len(ingredients),
                "ingredients": ingredients,
            })
        return result

    def _incomplete_analysis(self) -> dict:
        return {
            "status": "incomplete",
            "summary": "缺少成分，无法分析",
            "reasons": ["该产品暂未收录完整成分表，不能生成适配结论"],
            "highlights": [],
        }

    def _analyze_product(self, product: Product, profile: dict | None = None) -> dict:
        ingredients = product.ingredients or []
        if not ingredients:
            return self._incomplete_analysis()

        reasons: list[str] = []
        highlights = []
        status = "suitable"
        profile = profile or {}
        skin_type = profile.get("skin_type") or ""
        concerns = profile.get("skin_concerns") or []
        allergy_text = profile.get("known_allergies") or ""

        for item in ingredients:
            ingredient = item.ingredient
            tags = set(ingredient.tags or [])
            position = item.position
            ingredient_text = " ".join([
                ingredient.zh_name or "",
                ingredient.inci_name or "",
                " ".join(ingredient.aliases or []),
            ]).lower()
            is_high_position = position <= 8

            if allergy_text and self._text_matches_allergy(allergy_text, ingredient):
                status = "avoid"
                reasons.append(f"个人档案提到{allergy_text}，产品含有{ingredient.display_name()}")
                highlights.append(ingredient.to_dict(position))
                continue

            if skin_type == "敏感肌" and is_high_position and tags.intersection({"alcohol", "fragrance", "acid", "retinoid", "irritant"}):
                if status != "avoid":
                    status = "caution"
                reasons.append(f"敏感肌需留意第{position}位成分{ingredient.display_name()}")
                highlights.append(ingredient.to_dict(position))

            if is_high_position and tags.intersection({"alcohol", "fragrance", "acid", "retinoid"}):
                if status == "suitable":
                    status = "caution"
                reasons.append(f"{ingredient.display_name()}位置靠前，建议根据耐受情况谨慎使用")
                highlights.append(ingredient.to_dict(position))

            if any(item in concerns for item in ["痘痘", "闭口"]) and tags.intersection({"comedogenic", "heavy_oil"}):
                if status != "avoid":
                    status = "caution"
                reasons.append(f"痘痘/闭口人群需留意{ingredient.display_name()}的闷痘风险")
                highlights.append(ingredient.to_dict(position))

            if "brightening" in tags:
                highlights.append(ingredient.to_dict(position))

            if "uv_filter" in tags:
                highlights.append(ingredient.to_dict(position))

        unique_reasons = list(dict.fromkeys(reasons))
        unique_highlights = self._unique_highlights(highlights)
        summary_by_status = {
            "suitable": "未发现明显冲突成分",
            "caution": "存在需要留意的成分",
            "avoid": "与个人档案存在明确冲突",
        }
        return {
            "status": status,
            "summary": summary_by_status[status],
            "reasons": unique_reasons,
            "highlights": unique_highlights,
        }

    def _text_matches_allergy(self, allergy_text: str, ingredient) -> bool:
        normalized = allergy_text.lower()
        candidates = [ingredient.zh_name, ingredient.inci_name, *(ingredient.aliases or [])]
        if "酒精" in allergy_text and "alcohol" in (ingredient.tags or []):
            return True
        if "香精" in allergy_text and "fragrance" in (ingredient.tags or []):
            return True
        return any(candidate and candidate.lower() in normalized for candidate in candidates)

    def _unique_highlights(self, highlights: list[dict]) -> list[dict]:
        seen = set()
        unique = []
        for item in highlights:
            key = item["id"]
            if key in seen:
                continue
            seen.add(key)
            unique.append(item)
        return unique
