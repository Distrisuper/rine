"""Add date_sent and status_check_attempt_count to print_jobs

Revision ID: 016
Revises: 015
Create Date: 2026-04-15

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "016"
down_revision: Union[str, None] = "015"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("print_jobs", sa.Column("date_sent", sa.DateTime(), nullable=True))
    op.add_column(
        "print_jobs",
        sa.Column(
            "status_check_attempt_count",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
    )


def downgrade() -> None:
    op.drop_column("print_jobs", "status_check_attempt_count")
    op.drop_column("print_jobs", "date_sent")

