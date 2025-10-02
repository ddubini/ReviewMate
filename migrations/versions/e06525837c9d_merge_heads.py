"""merge heads

Revision ID: e06525837c9d
Revises: a1b2c3d4e5f6, dcfdf081c5f9
Create Date: 2025-09-29 02:25:59.631996

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e06525837c9d'
down_revision: Union[str, Sequence[str], None] = ('a1b2c3d4e5f6', 'dcfdf081c5f9')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
