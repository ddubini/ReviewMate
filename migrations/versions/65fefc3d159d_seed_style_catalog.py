from alembic import op
import sqlalchemy as sa
from datetime import datetime

# revision identifiers, used by Alembic.
revision = "a1b2c3d4e5f6"      # 이 파일의 실제 리비전 ID (알레믹이 생성해 둠)
down_revision = "36ff71a87bf4" # 직전 리비전 ID (실제 존재하는 파일의 revision 값)
branch_labels = None
depends_on = None

def upgrade():
    now = datetime.utcnow()
    table = sa.table(
        "style_catalog",
        sa.column("id", sa.Integer),
        sa.column("key", sa.String),
        sa.column("name", sa.String),
        sa.column("description", sa.Text),
        sa.column("example_snippet", sa.Text),
        sa.column("is_active", sa.Boolean),
        sa.column("created_at", sa.DateTime),
        sa.column("updated_at", sa.DateTime),
    )

    op.bulk_insert(
        table,
        [
            {
                "key": "friendly",
                "name": "친근한",
                "description": "따뜻하고 공감형 어투",
                "example_snippet": "처음 한 모금에서 기분이 좋아지는 맛이에요.",
                "is_active": True,
                "created_at": now,
                "updated_at": now,
            },
            {
                "key": "critical",
                "name": "날카로운",
                "description": "분석적이고 냉정한 어투",
                "example_snippet": "향은 좋지만 바디가 무너져 밸런스가 아쉽습니다.",
                "is_active": True,
                "created_at": now,
                "updated_at": now,
            },
            {
                "key": "witty",
                "name": "위트있는",
                "description": "재치 있고 가벼운 농담을 섞는 어투",
                "example_snippet": "칼로리는 0인 것 같은 행복, 두 번 주문할 뻔!",
                "is_active": True,
                "created_at": now,
                "updated_at": now,
            },
            {
                "key": "minimal",
                "name": "담백한",
                "description": "간결하고 군더더기 없는 어투",
                "example_snippet": "고소함이 선명하고 마무리는 깔끔합니다.",
                "is_active": True,
                "created_at": now,
                "updated_at": now,
            },
            {
                "key": "poetic",
                "name": "서정적",
                "description": "비유와 묘사가 풍부한 어투",
                "example_snippet": "따뜻한 빛처럼 스며드는 풍미가 오래 머뭅니다.",
                "is_active": True,
                "created_at": now,
                "updated_at": now,
            },
        ],
    )

def downgrade():
    op.execute("DELETE FROM style_catalog WHERE key IN ('friendly','critical','witty','minimal','poetic')")
