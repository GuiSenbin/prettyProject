"""add source url to products

Revision ID: 20260712_0007
Revises: 20260712_0006
Create Date: 2026-07-12 23:50:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "20260712_0007"
down_revision = "20260712_0006"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = {column["name"] for column in inspector.get_columns("products")}
    if "source_url" not in columns:
        op.add_column("products", sa.Column("source_url", sa.String(length=500), nullable=True))


def downgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    columns = {column["name"] for column in inspector.get_columns("products")}
    if "source_url" in columns:
        op.drop_column("products", "source_url")
