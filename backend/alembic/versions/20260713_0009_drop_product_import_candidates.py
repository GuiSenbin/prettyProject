"""drop product import candidate tables

Revision ID: 20260713_0009
Revises: e947615dbf1b
Create Date: 2026-07-13 21:20:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "20260713_0009"
down_revision = "e947615dbf1b"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if inspector.has_table("product_import_evidence"):
        op.drop_index(op.f("ix_product_import_evidence_candidate_id"), table_name="product_import_evidence")
        op.drop_index(op.f("ix_product_import_evidence_id"), table_name="product_import_evidence")
        op.drop_table("product_import_evidence")
    if inspector.has_table("product_import_candidates"):
        op.drop_index(op.f("ix_product_import_candidates_name"), table_name="product_import_candidates")
        op.drop_index(op.f("ix_product_import_candidates_id"), table_name="product_import_candidates")
        op.drop_table("product_import_candidates")


def downgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if not inspector.has_table("product_import_candidates"):
        op.create_table(
            "product_import_candidates",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("brand", sa.String(length=80), nullable=True),
            sa.Column("name", sa.String(length=160), nullable=False),
            sa.Column("category", sa.String(length=40), nullable=True),
            sa.Column("status", sa.String(length=24), nullable=False),
            sa.Column("source_type", sa.String(length=40), nullable=False),
            sa.Column("source_url", sa.String(length=500), nullable=False),
            sa.Column("source_title", sa.String(length=160), nullable=True),
            sa.Column("raw_ingredient_text", sa.Text(), nullable=False),
            sa.Column("ingredient_names", sa.JSON(), nullable=False),
            sa.Column("approved_product_id", sa.Integer(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.Column("updated_at", sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(["approved_product_id"], ["products.id"], ondelete="SET NULL"),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(op.f("ix_product_import_candidates_id"), "product_import_candidates", ["id"], unique=False)
        op.create_index(op.f("ix_product_import_candidates_name"), "product_import_candidates", ["name"], unique=False)
    if not inspector.has_table("product_import_evidence"):
        op.create_table(
            "product_import_evidence",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("candidate_id", sa.Integer(), nullable=False),
            sa.Column("evidence_type", sa.String(length=40), nullable=False),
            sa.Column("source_url", sa.String(length=500), nullable=False),
            sa.Column("raw_text", sa.Text(), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(["candidate_id"], ["product_import_candidates.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(op.f("ix_product_import_evidence_id"), "product_import_evidence", ["id"], unique=False)
        op.create_index(op.f("ix_product_import_evidence_candidate_id"), "product_import_evidence", ["candidate_id"], unique=False)
