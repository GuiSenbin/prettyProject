"""clean users table for baseline app

Revision ID: 20260705_0003
Revises: 20260705_0002
Create Date: 2026-07-05
"""
from alembic import op
import sqlalchemy as sa

revision = "20260705_0003"
down_revision = "20260705_0002"
branch_labels = None
depends_on = None


def _columns(bind, table_name: str) -> set[str]:
    inspector = sa.inspect(bind)
    if not inspector.has_table(table_name):
        return set()
    return {column["name"] for column in inspector.get_columns(table_name)}


def upgrade() -> None:
    bind = op.get_bind()
    columns = _columns(bind, "users")
    if not columns:
        return

    with op.batch_alter_table("users", recreate="always") as batch_op:
        if "phone" not in columns:
            batch_op.add_column(sa.Column("phone", sa.String(length=32), nullable=False, server_default=""))
        if "display_name" not in columns:
            batch_op.add_column(sa.Column("display_name", sa.String(length=50), nullable=False, server_default="智颜用户"))
        if "login_type" not in columns:
            batch_op.add_column(sa.Column("login_type", sa.String(length=20), nullable=False, server_default="phone"))
        for column_name in ("name", "age", "gender", "skin_type", "face_shape", "skin_tone", "concerns"):
            if column_name in columns:
                batch_op.drop_column(column_name)


def downgrade() -> None:
    bind = op.get_bind()
    columns = _columns(bind, "users")
    if not columns:
        return

    with op.batch_alter_table("users", recreate="always") as batch_op:
        if "name" not in columns:
            batch_op.add_column(sa.Column("name", sa.String(length=50), nullable=False, server_default="用户"))
        if "age" not in columns:
            batch_op.add_column(sa.Column("age", sa.String(length=20), nullable=True))
        if "gender" not in columns:
            batch_op.add_column(sa.Column("gender", sa.String(length=10), nullable=True))
        if "skin_type" not in columns:
            batch_op.add_column(sa.Column("skin_type", sa.String(length=20), nullable=True))
        if "face_shape" not in columns:
            batch_op.add_column(sa.Column("face_shape", sa.String(length=20), nullable=True))
        if "skin_tone" not in columns:
            batch_op.add_column(sa.Column("skin_tone", sa.String(length=20), nullable=True))
        if "concerns" not in columns:
            batch_op.add_column(sa.Column("concerns", sa.JSON(), nullable=True))
        for column_name in ("phone", "display_name", "login_type"):
            if column_name in columns:
                batch_op.drop_column(column_name)
