"""Drop print_type from print_jobs

Revision ID: 013
Revises: 012
Create Date: 2026-03-04

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '013'
down_revision: Union[str, None] = '012'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column('print_jobs', 'print_type')


def downgrade() -> None:
    op.add_column('print_jobs', sa.Column('print_type', sa.String(), nullable=True))
