"""Add template_id FK to channels

Revision ID: 012
Revises: 011
Create Date: 2026-03-02

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '012'
down_revision: Union[str, None] = '011'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('channels', sa.Column('template_id', sa.Integer(), nullable=True))
    op.create_foreign_key(
        'fk_channels_template_id',
        'channels',
        'templates',
        ['template_id'],
        ['id'],
    )


def downgrade() -> None:
    op.drop_constraint('fk_channels_template_id', 'channels', type_='foreignkey')
    op.drop_column('channels', 'template_id')
