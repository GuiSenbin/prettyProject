"""add product compliance fields

Revision ID: 20260713_0010
Revises: 20260713_0009
Create Date: 2026-07-13 23:40:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "20260713_0010"
down_revision = "20260713_0009"
branch_labels = None
depends_on = None


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


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = {column["name"] for column in inspector.get_columns("products")}
    if "registration_number" not in columns:
        op.add_column("products", sa.Column("registration_number", sa.String(length=80), nullable=True))
    if "brand_origin_country" not in columns:
        op.add_column("products", sa.Column("brand_origin_country", sa.String(length=40), nullable=True))

    products = sa.table(
        "products",
        sa.column("brand", sa.String()),
        sa.column("brand_origin_country", sa.String()),
    )
    for brand, country in BRAND_ORIGIN_COUNTRIES.items():
        bind.execute(
            products.update()
            .where(products.c.brand == brand)
            .where(products.c.brand_origin_country.is_(None))
            .values(brand_origin_country=country)
        )


def downgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = {column["name"] for column in inspector.get_columns("products")}
    if "brand_origin_country" in columns:
        op.drop_column("products", "brand_origin_country")
    if "registration_number" in columns:
        op.drop_column("products", "registration_number")
