"""add chat threads & messages

Revision ID: 43eef5bb328e
Revises: e6583710641c
Create Date: 2025-10-02 02:20:33.815185
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "43eef5bb328e"
down_revision: Union[str, Sequence[str], None] = "e6583710641c"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── chat threads ─────────────────────────────────────────────
    op.create_table(
        "review_chat_threads",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("request_id", sa.Integer(), sa.ForeignKey("review_requests.id"), nullable=True),
        sa.Column("style_id", sa.Integer(), sa.ForeignKey("style_catalog.id"), nullable=True),
        sa.Column("title", sa.String(length=255), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_review_chat_threads_user_id", "review_chat_threads", ["user_id"])
    op.create_index("ix_review_chat_threads_request_id", "review_chat_threads", ["request_id"])
    op.create_index("ix_review_chat_threads_style_id", "review_chat_threads", ["style_id"])

    # ── chat messages ────────────────────────────────────────────
    op.create_table(
        "review_chat_messages",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("thread_id", sa.Integer(), sa.ForeignKey("review_chat_threads.id", ondelete="CASCADE"), nullable=False),
        # assistant 메시지는 user_id가 없을 수 있으니 nullable=True 권장
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("role", sa.String(length=16), nullable=False),    # 'user' | 'assistant' 등
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_review_chat_messages_thread_id", "review_chat_messages", ["thread_id"])
    op.create_index("ix_review_chat_messages_user_id", "review_chat_messages", ["user_id"])
    op.create_index("ix_review_chat_messages_role", "review_chat_messages", ["role"])

    # (선택) 기존 자동 생성된 login_count default 변경이 끼어 있었다면 여기서 손대지 않아도 됩니다.
    # 기존 파일에 있던 alter_column은 제거합니다(불필요 충돌 방지).


def downgrade() -> None:
    op.drop_index("ix_review_chat_messages_role", table_name="review_chat_messages")
    op.drop_index("ix_review_chat_messages_user_id", table_name="review_chat_messages")
    op.drop_index("ix_review_chat_messages_thread_id", table_name="review_chat_messages")
    op.drop_table("review_chat_messages")

    op.drop_index("ix_review_chat_threads_style_id", table_name="review_chat_threads")
    op.drop_index("ix_review_chat_threads_request_id", table_name="review_chat_threads")
    op.drop_index("ix_review_chat_threads_user_id", table_name="review_chat_threads")
    op.drop_table("review_chat_threads")
