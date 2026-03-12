"""Make print_type nullable

Revision ID: 005
Revises: 003
Create Date: 2026-02-26

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '005'
down_revision: Union[str, None] = '003'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    with op.batch_alter_table('print_jobs') as batch_op:
        batch_op.alter_column('print_type', existing_type=sa.String(), nullable=True)


def downgrade() -> None:
    pass
