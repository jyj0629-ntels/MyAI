"""merge divergent heads

Revision ID: a1b2c3d4e5f6
Revises: 8c9e43daa47c, c31d0e8b69d4
Create Date: 2026-09-09 00:00:00.000000

"""
from typing import Sequence, Union


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = ('8c9e43daa47c', 'c31d0e8b69d4')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """No-op merge of two previously divergent migration branches."""
    pass


def downgrade() -> None:
    """No-op merge; downgrade must target one of the parent revisions explicitly."""
    pass
