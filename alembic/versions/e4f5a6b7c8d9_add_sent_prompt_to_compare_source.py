"""add sent_prompt column to compare_source_responses (per-provider tailored prompt)

Revision ID: e4f5a6b7c8d9
Revises: d3e4f5a6b7c8
Create Date: 2026-10-26 01:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e4f5a6b7c8d9'
down_revision: Union[str, Sequence[str], None] = 'd3e4f5a6b7c8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('compare_source_responses', sa.Column('sent_prompt', sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column('compare_source_responses', 'sent_prompt')
