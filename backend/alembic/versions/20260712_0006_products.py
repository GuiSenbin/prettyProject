"""create products module tables

Revision ID: 20260712_0006
Revises: 96b5381de25e
Create Date: 2026-07-12 23:30:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "20260712_0006"
down_revision = "96b5381de25e"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)

    if not inspector.has_table("products"):
        op.create_table(
            "products",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("brand", sa.String(length=80), nullable=True),
            sa.Column("name", sa.String(length=160), nullable=False),
            sa.Column("category", sa.String(length=40), nullable=True),
            sa.Column("image_url", sa.String(length=255), nullable=True),
            sa.Column("status", sa.String(length=24), nullable=False),
            sa.Column("source", sa.String(length=40), nullable=False),
            sa.Column("ingredient_source", sa.String(length=80), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.Column("updated_at", sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(op.f("ix_products_id"), "products", ["id"], unique=False)
        op.create_index(op.f("ix_products_name"), "products", ["name"], unique=False)

    if not inspector.has_table("ingredients"):
        op.create_table(
            "ingredients",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("inci_name", sa.String(length=120), nullable=False),
            sa.Column("zh_name", sa.String(length=120), nullable=False),
            sa.Column("aliases", sa.JSON(), nullable=False),
            sa.Column("tags", sa.JSON(), nullable=False),
            sa.Column("description", sa.Text(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.Column("updated_at", sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("inci_name", name="uq_ingredients_inci_name"),
        )
        op.create_index(op.f("ix_ingredients_id"), "ingredients", ["id"], unique=False)
        op.create_index(op.f("ix_ingredients_inci_name"), "ingredients", ["inci_name"], unique=True)

    if not inspector.has_table("product_ingredients"):
        op.create_table(
            "product_ingredients",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("product_id", sa.Integer(), nullable=False),
            sa.Column("ingredient_id", sa.Integer(), nullable=False),
            sa.Column("position", sa.Integer(), nullable=False),
            sa.Column("concentration_hint", sa.String(length=32), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(["ingredient_id"], ["ingredients.id"], ondelete="CASCADE"),
            sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("product_id", "ingredient_id", name="uq_product_ingredient"),
            sa.UniqueConstraint("product_id", "position", name="uq_product_ingredient_position"),
        )
        op.create_index(op.f("ix_product_ingredients_id"), "product_ingredients", ["id"], unique=False)

    if not inspector.has_table("user_products"):
        op.create_table(
            "user_products",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("user_id", sa.String(length=36), nullable=False),
            sa.Column("product_id", sa.Integer(), nullable=True),
            sa.Column("custom_name", sa.String(length=160), nullable=True),
            sa.Column("status", sa.String(length=24), nullable=False),
            sa.Column("source", sa.String(length=32), nullable=False),
            sa.Column("notes", sa.Text(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.Column("updated_at", sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(["product_id"], ["products.id"], ondelete="SET NULL"),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(op.f("ix_user_products_id"), "user_products", ["id"], unique=False)
        op.create_index(op.f("ix_user_products_user_id"), "user_products", ["user_id"], unique=False)


def downgrade():
    op.drop_index(op.f("ix_user_products_user_id"), table_name="user_products")
    op.drop_index(op.f("ix_user_products_id"), table_name="user_products")
    op.drop_table("user_products")
    op.drop_index(op.f("ix_product_ingredients_id"), table_name="product_ingredients")
    op.drop_table("product_ingredients")
    op.drop_index(op.f("ix_ingredients_inci_name"), table_name="ingredients")
    op.drop_index(op.f("ix_ingredients_id"), table_name="ingredients")
    op.drop_table("ingredients")
    op.drop_index(op.f("ix_products_name"), table_name="products")
    op.drop_index(op.f("ix_products_id"), table_name="products")
    op.drop_table("products")
