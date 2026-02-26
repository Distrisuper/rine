"""Drop printer_type column from printers

Revision ID: 009
Revises: 008
Create Date: 2026-02-26

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = '009'
down_revision: Union[str, None] = '008'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_column('printers', 'printer_type')


def downgrade() -> None:
    op.add_column('printers', sa.Column('printer_type', sa.String(), nullable=True))
