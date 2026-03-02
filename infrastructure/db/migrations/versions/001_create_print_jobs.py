"""Create print_jobs table

Revision ID: 001
Revises: 
Create Date: 2026-02-26

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import Column, Integer, String, DateTime, Text, Index

# revision identifiers, used by Alembic.
revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'print_jobs',
        Column('id', Integer, primary_key=True, autoincrement=True),
        Column('client_id', String, nullable=True),
        Column('client_code', String, nullable=False),
        Column('client_name', String, nullable=False),
        Column('print_type', String, nullable=False),
        Column('status', String, nullable=False, server_default='pending'),
        Column('print_count', Integer, nullable=False, server_default='0'),
        Column('host', Integer, nullable=True),
        Column('date_created', DateTime, nullable=False, server_default=sa.func.now()),
        Column('date_started', DateTime, nullable=True),
        Column('date_processed', DateTime, nullable=True),
        Column('payload', Text, nullable=False),
        Column('printer_name', String, nullable=True),
        Column('error_message', Text, nullable=True),
    )
    
    op.create_index(
        'idx_print_jobs_status_created',
        'print_jobs',
        ['status', 'date_created'],
        unique=False
    )


def downgrade() -> None:
    op.drop_index('idx_print_jobs_status_created', table_name='print_jobs')
    op.drop_table('print_jobs')
