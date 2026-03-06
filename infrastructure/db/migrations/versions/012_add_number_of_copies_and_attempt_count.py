"""Add number_of_copies and attempt_count to print_jobs

Revision ID: 012
Revises: 011
Create Date: 2026-03-04

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '012'
down_revision: Union[str, None] = '011'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('print_jobs', sa.Column('number_of_copies', sa.Integer(), nullable=False, server_default='1'))
    op.add_column('print_jobs', sa.Column('attempt_count', sa.Integer(), nullable=False, server_default='0'))


def downgrade() -> None:
    op.drop_column('print_jobs', 'attempt_count')
    op.drop_column('print_jobs', 'number_of_copies')
