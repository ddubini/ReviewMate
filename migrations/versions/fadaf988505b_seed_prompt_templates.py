"""seed prompt templates

Revision ID: fadaf988505b
Revises: e06525837c9d
Create Date: 2025-09-29 02:44:58.527101

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'fadaf988505b'
down_revision: Union[str, Sequence[str], None] = 'e06525837c9d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
