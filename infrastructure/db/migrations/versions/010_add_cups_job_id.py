"""Add cups_job_id to print_jobs

Revision ID: 010
Revises: 009
Create Date: 2026-02-27

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '010'
down_revision: Union[str, None] = '009'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('print_jobs', sa.Column('cups_job_id', sa.Integer(), nullable=True))


def downgrade() -> None:
    op.drop_column('print_jobs', 'cups_job_id')
