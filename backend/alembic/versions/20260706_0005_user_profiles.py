"""create user profiles

Revision ID: 20260706_0005
Revises: 20260705_0004
Create Date: 2026-07-06 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

revision = "20260706_0005"
down_revision = "20260705_0004"
branch_labels = None
depends_on = None


def upgrade():
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    if not inspector.has_table("user_profiles"):
        op.create_table(
            "user_profiles",
            sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
            sa.Column("user_id", sa.String(length=36), nullable=False),
            sa.Column("gender", sa.String(length=12), nullable=True),
            sa.Column("age", sa.Integer(), nullable=True),
            sa.Column("skin_type", sa.String(length=32), nullable=True),
            sa.Column("skin_tone", sa.String(length=32), nullable=True),
            sa.Column("face_shape", sa.String(length=32), nullable=True),
            sa.Column("skin_concerns", sa.JSON(), nullable=False, server_default="[]"),
            sa.Column("known_allergies", sa.Text(), nullable=True),
            sa.Column("period_acne", sa.Boolean(), nullable=True),
            sa.Column("last_period_start", sa.Date(), nullable=True),
            sa.Column("cycle_length_days", sa.Integer(), nullable=True),
            sa.Column("pregnancy_status", sa.String(length=32), nullable=True),
            sa.Column("preference_notes", sa.Text(), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.Column("updated_at", sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
            sa.UniqueConstraint("user_id", name="uq_user_profiles_user_id"),
        )
    index_names = {index["name"] for index in inspector.get_indexes("user_profiles")}
    if op.f("ix_user_profiles_id") not in index_names:
        op.create_index(op.f("ix_user_profiles_id"), "user_profiles", ["id"], unique=False)


def downgrade():
    op.drop_index(op.f("ix_user_profiles_id"), table_name="user_profiles")
    op.drop_table("user_profiles")
