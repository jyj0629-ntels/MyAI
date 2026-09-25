"""merge multiple heads (forbidden_terms chain + provider_response_path chain)

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6, c31d0e8b69d4
Create Date: 2026-09-26 10:05:00.000000

"""
from typing import Sequence, Union


# revision identifiers, used by Alembic.
revision: str = 'b2c3d4e5f6a7'
down_revision: Union[str, Sequence[str], None] = ('a1b2c3d4e5f6', 'c31d0e8b69d4')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Merge revision - no schema changes."""
    pass


def downgrade() -> None:
    """Merge revision - no schema changes."""
    pass
