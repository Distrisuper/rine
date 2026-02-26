"""Create printers table

Revision ID: 006
Revises: 005
Create Date: 2026-02-26

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import Column, Integer, String, Boolean, DateTime, func


revision: str = '006'
down_revision: Union[str, None] = '005'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'printers',
        Column('id', Integer, primary_key=True, autoincrement=True),
        Column('name', String, nullable=False),
        Column('printer_type', String, nullable=False),
        Column('is_active', Boolean, nullable=False, server_default='1'),
        Column('created_at', DateTime, server_default=func.now()),
    )


def downgrade() -> None:
    op.drop_table('printers')
