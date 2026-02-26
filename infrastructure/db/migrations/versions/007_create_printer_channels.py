"""Create printer_channels table

Revision ID: 007
Revises: 006
Create Date: 2026-02-26

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey


revision: str = '007'
down_revision: Union[str, None] = '006'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'printer_channels',
        Column('printer_id', Integer, ForeignKey('printers.id'), primary_key=True),
        Column('channel', Integer, primary_key=True),
        Column('description', String, nullable=True),
        Column('is_active', Boolean, nullable=False, server_default='1'),
    )


def downgrade() -> None:
    op.drop_table('printer_channels')
