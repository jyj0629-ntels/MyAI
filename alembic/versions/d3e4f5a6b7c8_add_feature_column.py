"""add feature column to conversation and chat_history (split history per feature)

Revision ID: d3e4f5a6b7c8
Revises: c2d3e4f5a6b7
Create Date: 2026-10-26 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd3e4f5a6b7c8'
down_revision: Union[str, Sequence[str], None] = 'c2d3e4f5a6b7'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('conversation', sa.Column('feature', sa.String(length=20), nullable=False, server_default='myai'))
    op.add_column('chat_history', sa.Column('feature', sa.String(length=20), nullable=False, server_default='myai'))


def downgrade() -> None:
    op.drop_column('chat_history', 'feature')
    op.drop_column('conversation', 'feature')
