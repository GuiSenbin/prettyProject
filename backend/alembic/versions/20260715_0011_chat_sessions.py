"""add chat sessions and messages

Revision ID: 20260715_0011
Revises: 20260713_0010
Create Date: 2026-07-15 22:40:00.000000

"""
from alembic import op
import sqlalchemy as sa


revision = "20260715_0011"
down_revision = "20260713_0010"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "chat_sessions",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("title", sa.String(length=80), nullable=False),
        sa.Column("title_edited", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column("deleted_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_chat_sessions_id", "chat_sessions", ["id"])
    op.create_index("ix_chat_sessions_user_id", "chat_sessions", ["user_id"])

    op.create_table(
        "chat_messages",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("session_id", sa.Integer(), nullable=False),
        sa.Column("role", sa.String(length=20), nullable=False),
        sa.Column("content_text", sa.Text(), nullable=False),
        sa.Column("structured_payload", sa.JSON(), nullable=True),
        sa.Column("intent", sa.String(length=40), nullable=True),
        sa.Column("subject_type", sa.String(length=40), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["session_id"], ["chat_sessions.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_chat_messages_id", "chat_messages", ["id"])
    op.create_index("ix_chat_messages_session_id", "chat_messages", ["session_id"])

    op.create_table(
        "chat_question_logs",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.String(length=36), nullable=False),
        sa.Column("session_id", sa.Integer(), nullable=True),
        sa.Column("raw_question", sa.Text(), nullable=False),
        sa.Column("normalized_question", sa.Text(), nullable=False),
        sa.Column("intent", sa.String(length=40), nullable=True),
        sa.Column("subject_type", sa.String(length=40), nullable=True),
        sa.Column("context_used", sa.JSON(), nullable=False),
        sa.Column("answer_title", sa.String(length=120), nullable=True),
        sa.Column("source", sa.String(length=40), nullable=False, server_default="local_rule"),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["session_id"], ["chat_sessions.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_chat_question_logs_id", "chat_question_logs", ["id"])
    op.create_index("ix_chat_question_logs_user_id", "chat_question_logs", ["user_id"])


def downgrade():
    op.drop_index("ix_chat_question_logs_user_id", table_name="chat_question_logs")
    op.drop_index("ix_chat_question_logs_id", table_name="chat_question_logs")
    op.drop_table("chat_question_logs")
    op.drop_index("ix_chat_messages_session_id", table_name="chat_messages")
    op.drop_index("ix_chat_messages_id", table_name="chat_messages")
    op.drop_table("chat_messages")
    op.drop_index("ix_chat_sessions_user_id", table_name="chat_sessions")
    op.drop_index("ix_chat_sessions_id", table_name="chat_sessions")
    op.drop_table("chat_sessions")
