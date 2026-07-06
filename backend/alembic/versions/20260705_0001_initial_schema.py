"""initial clean user schema

Revision ID: 20260705_0001
Revises:
Create Date: 2026-07-05
"""
from alembic import op
import sqlalchemy as sa

revision = "20260705_0001"
down_revision = None
branch_labels = None
depends_on = None


def _has_table(bind, table_name: str) -> bool:
    return sa.inspect(bind).has_table(table_name)


def _has_index(bind, table_name: str, index_name: str) -> bool:
    return any(index["name"] == index_name for index in sa.inspect(bind).get_indexes(table_name))


def upgrade() -> None:
    bind = op.get_bind()
    if not _has_table(bind, "users"):
        op.create_table(
            "users",
            sa.Column("id", sa.String(length=36), nullable=False),
            sa.Column("phone", sa.String(length=32), nullable=False),
            sa.Column("display_name", sa.String(length=50), nullable=False),
            sa.Column("login_type", sa.String(length=20), nullable=False),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.Column("updated_at", sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint("id"),
        )
    if not _has_index(bind, "users", "ix_users_id"):
        op.create_index("ix_users_id", "users", ["id"], unique=False)


def downgrade() -> None:
    bind = op.get_bind()
    if _has_table(bind, "users"):
        op.drop_index("ix_users_id", table_name="users")
        op.drop_table("users")
