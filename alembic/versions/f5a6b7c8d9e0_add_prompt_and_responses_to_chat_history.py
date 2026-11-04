"""add generated_prompt and provider_responses_json to chat_history

Revision ID: f5a6b7c8d9e0
Revises: e4f5a6b7c8d9
Create Date: 2026-10-27 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f5a6b7c8d9e0'
down_revision: Union[str, Sequence[str], None] = 'e4f5a6b7c8d9'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('chat_history', sa.Column('generated_prompt', sa.Text(), nullable=True))
    op.add_column('chat_history', sa.Column('provider_responses_json', sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column('chat_history', 'provider_responses_json')
    op.drop_column('chat_history', 'generated_prompt')
