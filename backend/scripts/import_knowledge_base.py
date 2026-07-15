import json
import os
import sys
import shutil

# 将项目根目录添加到 sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.core.database import SessionLocal
from app.modules.products.models import Product, Ingredient, ProductIngredient

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

REGISTRATION_NUMBERS = {
    "理肤泉净化舒缓洁面啫喱": "演示待核验-0001",
    "芙丽芳丝净润洗面霜": "国妆网备进字(沪)2020003544",
    "宝拉珍选大地之源洁面凝胶": "国妆备进字J20156734",
    "香奈儿山茶花洁面乳": "国妆网备进字(沪)2018000608",
    "CPB肌肤之钥光采洗面膏": "演示待核验-0005",
    "适乐肤水杨酸洁面": "演示待核验-0006",
    "至本舒颜修护洁面乳": "演示待核验-0007",
    "优色林舒安清润洁面乳": "国妆备进字J20114570",
    "eltaMD氨基酸泡沫洁面": "国妆网备进字(沪)2020009992",
    "海蓝之谜璀璨净澈洁面泡沫": "国妆网备进字(沪)2021002456",
    "修丽可色修精华": "国妆网备进字(沪)202300783",
    "雅诗兰黛第七代小棕瓶": "国妆网备进字(沪)2020003600",
    "兰蔻第二代小黑瓶": "国妆网备进字(沪)2019002144",
    "娇韵诗双萃精华": "演示待核验-0014",
    "海蓝之谜浓缩修护精华露": "演示待核验-0015",
    "倩碧302美白镭射瓶": "演示待核验-0016",
    "资生堂红妍肌活精华露": "国妆备进字J20144201",
    "修丽可CE经典抗氧精华": "演示待核验-0018",
    "理肤泉B5多效保湿精华": "演示待核验-0019",
    "赫莲娜绿宝瓶精华": "国妆备进字J20172068",
    "科颜氏高保湿面霜": "演示待核验-0021",
    "海蓝之谜精华面霜": "国妆备进字J20165515",
    "SK-II神仙水": "国妆网备进字(沪)2021000104",
    "兰蔻极光水": "国妆网备进字(沪)2023008829",
    "赫莲娜黑绷带面霜": "国妆网备进字(沪)2023002958",
    "雅诗兰黛原生液": "国妆备进字J20137585",
    "娇兰复原蜜": "国妆备进字J20175509",
    "理肤泉B5修复霜": "国妆网备进字(沪)2021002727",
    "IPSA茵芙莎流金水": "演示待核验-0029",
    "资生堂悦薇水乳": "演示待核验-0030",
    "安热沙小金瓶防晒乳": "演示待核验-0031",
    "兰蔻菁纯防晒": "演示待核验-0032",
    "理肤泉大哥大防晒": "演示待核验-0033",
    "资生堂蓝胖子防晒": "演示待核验-0034",
    "嘉娜宝ALLIE防晒霜": "演示待核验-0035",
    "修丽可发光防晒": "演示待核验-0036",
    "CPB御龄防晒乳霜": "演示待核验-0037",
    "黛珂多重防晒乳": "演示待核验-0038",
    "EltaMD清透护肤防晒乳": "演示待核验-0039",
    "自然哲理防晒面霜": "演示待核验-0040",
    "欧莱雅金致臻颜奢养粉妍防晒乳": "国妆特字G20170937",
    "SK-II前男友面膜": "演示待核验-0041",
    "香缇卡钻石面膜": "演示待核验-0042",
    "菲洛嘉十全大补面膜": "国妆网备进字(京)2019000281",
    "复刻雅诗兰黛钢铁侠面膜": "国妆备进字J20153255",
    "理肤泉B5多效保湿面膜": "演示待核验-0045",
    "法尔曼幸福面膜": "演示待核验-0046",
    "馥蕾诗玫瑰润泽保湿舒缓面膜": "国妆网备进字(沪)2019007126",
    "蒂佳婷蓝丸面膜": "国妆网备进字(沪)2020004960",
    "科颜氏白泥净肤面膜": "国妆备进字J20155760",
    "欧莱雅安瓶面膜": "演示待核验-0050",
    "雅诗兰黛DW持妆粉底液": "国妆备进字J20186020",
    "阿玛尼权力粉底液": "演示待核验-0052",
    "兰蔻菁纯粉底液": "演示待核验-0053",
    "YSL恒久粉底液": "演示待核验-0054",
    "CPB光缎粉霜": "演示待核验-0055",
    "NARS超模粉底液": "演示待核验-0056",
    "魅可定制无瑕粉底液": "演示待核验-0057",
    "植村秀小方瓶粉底液": "演示待核验-0058",
    "SUQQU记忆塑形粉霜": "演示待核验-0059",
    "芭比波朗虫草粉底液": "演示待核验-0060",
    "迪奥999烈艳蓝金唇膏": "演示待核验-0061",
    "香奈儿炫亮魅力唇膏": "国妆网备进字(沪)2021002797",
    "TF黑管唇膏": "演示待核验-0063",
    "YSL小金条口红": "演示待核验-0064",
    "NARS腮红": "国妆网备进字(沪)2024000635",
    "MAC生姜高光": "演示待核验-0066",
    "CT四色眼影盘": "国妆网备进字(沪)2023008544",
    "UD牛郎单色眼影": "国妆网备进字(沪)2022002306",
    "纪梵希四宫格散粉": "国妆网备进字(沪)2021002562",
    "完美日记小细跟口红": "粤G妆网备字2021037460",
}


def import_seed_data():
    db = SessionLocal()
    seed_file_path = os.path.join(os.path.dirname(__file__), 'seed_products.json')

    # 静态资源源目录与目标目录
    source_image_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../frontend/src/assets/product'))
    target_image_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../static/product'))

    # 扫描前端的所有产品图片并升序排序
    image_files = []
    if os.path.exists(source_image_dir):
        image_files = sorted([f for f in os.listdir(source_image_dir) if f.lower().endswith('.png')])

    # 创建后端静态图片目录
    os.makedirs(target_image_dir, exist_ok=True)

    with open(seed_file_path, 'r', encoding='utf-8') as f:
        categories_data = json.load(f)

    try:
        total_products = 0
        global_product_index = 0

        for category_data in categories_data:
            category_name = category_data['category']
            products = category_data['products']

            for prod_data in products:
                # 确定对应本地图片的 URL
                db_image_url = prod_data['image_url']
                if db_image_url.startswith("/static/product/"):
                    img_filename = os.path.basename(db_image_url)
                    src_path = os.path.join(source_image_dir, img_filename)
                    dst_path = os.path.join(target_image_dir, img_filename)
                    if os.path.exists(src_path):
                        try:
                            shutil.copy(src_path, dst_path)
                        except Exception as copy_err:
                            print(f"Failed to copy image {img_filename}: {copy_err}")
                elif global_product_index < len(image_files):
                    img_filename = image_files[global_product_index]
                    src_path = os.path.join(source_image_dir, img_filename)
                    dst_path = os.path.join(target_image_dir, img_filename)

                    # 复制图片文件到后端静态目录
                    try:
                        shutil.copy(src_path, dst_path)
                    except Exception as copy_err:
                        print(f"Failed to copy image {img_filename}: {copy_err}")

                    db_image_url = f"/static/product/{img_filename}"
                    # 递增产品索引以匹配下一张自动编号图片
                    global_product_index += 1

                # 检查产品是否已存在
                product = db.query(Product).filter(Product.name == prod_data['name']).first()
                if not product:
                    product = Product(
                        name=prod_data['name'],
                        brand=prod_data['brand'],
                        category=category_name,
                        image_url=db_image_url,
                        registration_number=REGISTRATION_NUMBERS.get(prod_data['name']),
                        brand_origin_country=BRAND_ORIGIN_COUNTRIES.get(prod_data['brand']),
                    )
                    db.add(product)
                    db.commit()
                    db.refresh(product)
                else:
                    # 强制更新已存在产品的 image_url 为清洗后的本地静态图 URL
                    product.image_url = db_image_url
                    product.registration_number = REGISTRATION_NUMBERS.get(prod_data['name'])
                    if not product.brand_origin_country:
                        product.brand_origin_country = BRAND_ORIGIN_COUNTRIES.get(prod_data['brand'])
                    db.commit()
                    db.refresh(product)

                # 处理成分
                for idx, ing_data in enumerate(prod_data['ingredients']):
                    inci_name = ing_data['inci_name']
                    # 检查成分是否已存在 (以 INCI name 为准)
                    ingredient = db.query(Ingredient).filter(Ingredient.inci_name == inci_name).first()

                    if not ingredient:
                        ingredient = Ingredient(
                            inci_name=inci_name,
                            zh_name=ing_data['zh_name'],
                            safety_level=ing_data['safety_level'],
                            purposes=ing_data['purposes']
                        )
                        db.add(ingredient)
                        db.commit()
                        db.refresh(ingredient)

                    # 关联产品和成分
                    assoc = db.query(ProductIngredient).filter(
                        ProductIngredient.product_id == product.id,
                        ProductIngredient.ingredient_id == ingredient.id
                    ).first()

                    if not assoc:
                        assoc = ProductIngredient(
                            product_id=product.id,
                            ingredient_id=ingredient.id,
                            position=idx + 1
                        )
                        db.add(assoc)

                db.commit()
                total_products += 1
                print(f"[{category_name}] Imported/Updated: {product.name} -> {product.image_url}")

        print(f"\nSuccessfully imported/updated {total_products} products!")

    except Exception as e:
        db.rollback()
        print(f"Error importing data: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    print("Starting import knowledge base seed data...")
    import_seed_data()
