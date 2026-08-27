"""add chat history table

Revision ID: 372e3481a7cb
Revises: e80d73d5462e
Create Date: 2026-08-25 14:11:10.677557

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '372e3481a7cb'
down_revision: Union[str, Sequence[str], None] = 'e80d73d5462e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
