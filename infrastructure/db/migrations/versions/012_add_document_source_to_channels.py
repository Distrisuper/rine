"""Add document_source to channels

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
    op.add_column('channels', sa.Column('document_source', sa.String, nullable=False, server_default='INTERNAL'))


def downgrade() -> None:
    op.drop_column('channels', 'document_source')
