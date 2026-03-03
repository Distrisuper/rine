"""Create channels table

Revision ID: 008
Revises: 007
Create Date: 2026-02-26

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, func


revision: str = '008'
down_revision: Union[str, None] = '007'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'channels',
        Column('id', Integer, primary_key=True, autoincrement=True),
        Column('channel_number', Integer, nullable=False, unique=True),
        Column('description', String, nullable=True),
        Column('is_active', Boolean, nullable=False, server_default='1'),
        Column('template_id', Integer, ForeignKey('templates.id'), nullable=True),
        Column('created_at', DateTime, server_default=func.now()),
    )
    op.create_index('ix_channels_template_id', 'channels', ['template_id'])


def downgrade() -> None:
    try:
        op.drop_index('ix_channels_template_id', table_name='channels')
    except Exception:
        pass
    op.drop_table('channels')
