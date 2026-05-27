"""Add landscape label template

Revision ID: 015
Revises: 014
Create Date: 2026-03-23

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "015"
down_revision: Union[str, None] = "014"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

TEMPLATE_NAME = "Zebra Label Landscape 90"
TEMPLATE_FILE_PATH = "labels/zebra_label_landscape_90.zpl"


def upgrade() -> None:
    bind = op.get_bind()
    bind.execute(
        sa.text(
            """
            INSERT INTO templates (name, file_path)
            SELECT :name, :file_path
            WHERE NOT EXISTS (
                SELECT 1
                FROM templates
                WHERE name = :name
            )
            """
        ),
        {"name": TEMPLATE_NAME, "file_path": TEMPLATE_FILE_PATH},
    )


def downgrade() -> None:
    bind = op.get_bind()
    bind.execute(
        sa.text(
            """
            DELETE FROM templates
            WHERE name = :name AND file_path = :file_path
            """
        ),
        {"name": TEMPLATE_NAME, "file_path": TEMPLATE_FILE_PATH},
    )
