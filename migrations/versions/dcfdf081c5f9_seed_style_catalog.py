"""seed style_catalog

Revision ID: dcfdf081c5f9
Revises: 36ff71a87bf4
Create Date: 2025-09-29 02:16:23.758776

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'dcfdf081c5f9'
down_revision: Union[str, Sequence[str], None] = '36ff71a87bf4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
