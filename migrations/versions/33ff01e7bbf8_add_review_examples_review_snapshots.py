"""add review_examples & review_snapshots

Revision ID: 33ff01e7bbf8
Revises: 43eef5bb328e
Create Date: 2025-10-02 02:35:00
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "33ff01e7bbf8"
down_revision: Union[str, Sequence[str], None] = "43eef5bb328e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # review_examples
    op.create_table(
        "review_examples",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("style_key", sa.String(50), nullable=True, index=False),
        sa.Column("persona_id", sa.Integer(), nullable=True),
        sa.Column("title", sa.String(255), nullable=True),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("quality_score", sa.Float(), nullable=True, server_default=sa.text("1.0")),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["persona_id"], ["personas.id"]),
    )
    op.create_index("ix_review_examples_style_key", "review_examples", ["style_key"], unique=False)
    op.create_index("ix_review_examples_persona_id", "review_examples", ["persona_id"], unique=False)

    # review_snapshots
    op.create_table(
        "review_snapshots",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("request_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("style_key", sa.String(50), nullable=True),
        sa.Column("persona_id", sa.Integer(), nullable=True),
        sa.Column("prompt_key", sa.String(50), nullable=False),
        sa.Column("payload_json", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.ForeignKeyConstraint(["request_id"], ["review_requests.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["persona_id"], ["personas.id"]),
    )
    op.create_index("ix_review_snapshots_request_id", "review_snapshots", ["request_id"], unique=False)
    op.create_index("ix_review_snapshots_user_id", "review_snapshots", ["user_id"], unique=False)
    op.create_index("ix_review_snapshots_style_key", "review_snapshots", ["style_key"], unique=False)
    op.create_index("ix_review_snapshots_prompt_key", "review_snapshots", ["prompt_key"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_review_snapshots_prompt_key", table_name="review_snapshots")
    op.drop_index("ix_review_snapshots_style_key", table_name="review_snapshots")
    op.drop_index("ix_review_snapshots_user_id", table_name="review_snapshots")
    op.drop_index("ix_review_snapshots_request_id", table_name="review_snapshots")
    op.drop_table("review_snapshots")

    op.drop_index("ix_review_examples_persona_id", table_name="review_examples")
    op.drop_index("ix_review_examples_style_key", table_name="review_examples")
    op.drop_table("review_examples")
