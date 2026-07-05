"""clean baseline compatibility no-op

Revision ID: 20260705_0002
Revises: 20260705_0001
Create Date: 2026-07-05
"""

revision = "20260705_0002"
down_revision = "20260705_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """保留迁移链，纯净版不再创建聊天业务表。"""


def downgrade() -> None:
    """兼容 no-op。"""
