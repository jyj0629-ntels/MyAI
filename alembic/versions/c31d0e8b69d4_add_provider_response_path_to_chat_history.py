"""add provider_response_path to chat_history

Revision ID: c31d0e8b69d4
Revises: 154d1238b937
Create Date: 2026-09-07 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "c31d0e8b69d4"
down_revision: Union[str, Sequence[str], None] = "154d1238b937"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('chat_history', sa.Column('provider_response_path', sa.String(length=255), nullable=True))


def downgrade() -> None:
    op.drop_column('chat_history', 'provider_response_path')
