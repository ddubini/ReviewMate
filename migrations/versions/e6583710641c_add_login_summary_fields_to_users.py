"""add login summary fields to users

Revision ID: e6583710641c
Revises: 6dc5f9b9260d
Create Date: 2025-10-02 01:58:39.594905
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "e6583710641c"
down_revision: Union[str, Sequence[str], None] = "6dc5f9b9260d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column("users", sa.Column("last_login_at", sa.DateTime(), nullable=True))
    op.add_column("users", sa.Column("last_login_ip", sa.String(length=255), nullable=True))
    op.add_column("users", sa.Column("last_login_ua", sa.String(length=500), nullable=True))
    # 기존 행들 때문에 NOT NULL 컬럼은 기본값을 달아주는 게 안전
    op.add_column(
        "users",
        sa.Column("login_count", sa.Integer(), nullable=False, server_default="0"),
    )
    # (선택) 기본값 제거하려면 아래 주석 해제
    # op.alter_column("users", "login_count", server_default=None)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("users", "login_count")
    op.drop_column("users", "last_login_ua")
    op.drop_column("users", "last_login_ip")
    op.drop_column("users", "last_login_at")

