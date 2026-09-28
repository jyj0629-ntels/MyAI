"""add compare tables (compare_histories, compare_source_responses)

Also merges the two existing heads (8c9e43daa47c, c31d0e8b69d4) into a single head.

Revision ID: b1c2d3e4f5a6
Revises: 8c9e43daa47c, c31d0e8b69d4
Create Date: 2026-09-11 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b1c2d3e4f5a6'
down_revision: Union[str, Sequence[str], None] = ('8c9e43daa47c', 'c31d0e8b69d4')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'compare_histories',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('user_prompt', sa.Text(), nullable=False),
        sa.Column('summary_result', sa.Text(), nullable=True),
        sa.Column('llm_model_used', sa.String(length=100), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='PROCESSING'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_table(
        'compare_source_responses',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('history_id', sa.Integer(), nullable=False),
        sa.Column('ai_provider', sa.String(length=50), nullable=False),
        sa.Column('raw_response', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='SUCCESS'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['history_id'], ['compare_histories.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_compare_source_responses_history_id', 'compare_source_responses', ['history_id'])


def downgrade() -> None:
    op.drop_index('ix_compare_source_responses_history_id', table_name='compare_source_responses')
    op.drop_table('compare_source_responses')
    op.drop_table('compare_histories')
