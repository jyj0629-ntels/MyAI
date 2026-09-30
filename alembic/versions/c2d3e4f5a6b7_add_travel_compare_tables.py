"""add travel compare tables (travel_compare_histories, travel_round_responses)

Revision ID: c2d3e4f5a6b7
Revises: b1c2d3e4f5a6
Create Date: 2026-09-11 01:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c2d3e4f5a6b7'
down_revision: Union[str, Sequence[str], None] = 'b1c2d3e4f5a6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'travel_compare_histories',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('user_prompt', sa.Text(), nullable=False),
        sa.Column('round2_prompt', sa.Text(), nullable=True),
        sa.Column('final_result', sa.Text(), nullable=True),
        sa.Column('llm_model_used', sa.String(length=100), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='PROCESSING'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )

    op.create_table(
        'travel_round_responses',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('history_id', sa.Integer(), nullable=False),
        sa.Column('round_no', sa.Integer(), nullable=False),
        sa.Column('ai_provider', sa.String(length=50), nullable=False),
        sa.Column('raw_response', sa.Text(), nullable=True),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False, server_default='SUCCESS'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['history_id'], ['travel_compare_histories.id'], ),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_travel_round_responses_history_id', 'travel_round_responses', ['history_id'])


def downgrade() -> None:
    op.drop_index('ix_travel_round_responses_history_id', table_name='travel_round_responses')
    op.drop_table('travel_round_responses')
    op.drop_table('travel_compare_histories')
