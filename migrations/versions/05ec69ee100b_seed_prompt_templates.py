"""seed prompt templates

Revision ID: 05ec69ee100b
Revises: fadaf988505b
Create Date: 2025-09-29 02:53:49.267312
"""
from typing import Sequence, Union
from datetime import datetime

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "05ec69ee100b"
down_revision: Union[str, Sequence[str], None] = "fadaf988505b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    now = datetime.utcnow()

    # review_prompt_templates 테이블에 맞춘 가상 테이블 정의
    t = sa.table(
        "review_prompt_templates",
        sa.column("prompt_key", sa.String),
        sa.column("style_key", sa.String),
        sa.column("template", sa.Text),
        sa.column("created_at", sa.DateTime),
        sa.column("updated_at", sa.DateTime),
    )

    op.bulk_insert(
        t,
        [
            {
                "prompt_key": "first_review",
                "style_key": None,
                "template": (
                    "다음 정보를 바탕으로 {{ tone_prefix }} 한국어 리뷰를 작성해줘.\n"
                    "- 가게: {{ restaurant_name or '이름없음' }}\n"
                    "- 음식 종류: {{ cuisine_type or '미상' }}\n"
                    "- 가격대: {{ price_min or '-' }} ~ {{ price_max or '-' }}\n"
                    "- 요구사항(톤/금지어 등): {{ requirements or '없음' }}\n"
                    "요구사항을 지키되, 매끄럽고 자연스럽게 써줘."
                ),
                "created_at": now,
                "updated_at": now,
            },
            {
                "prompt_key": "chat_reply",
                "style_key": None,
                "template": (
                    "{{ tone_prefix }} 아래 대화 맥락을 고려해 한글로 답장해줘.\n"
                    "{% for t in history %}\n"
                    "{{ '[사용자]' if t.role=='user' else '[어시스턴트]' }}: {{ t.content }}\n"
                    "{% endfor %}\n"
                    "과장/모욕/금지어를 피하고, 간결하고 유익하게."
                ),
                "created_at": now,
                "updated_at": now,
            },
        ],
    )


def downgrade() -> None:
    op.execute(
        "DELETE FROM review_prompt_templates "
        "WHERE prompt_key IN ('first_review','chat_reply')"
    )
