"""add request_hash column and composite index

Revision ID: 002
Revises: 001
Create Date: 2026-04-14

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "evaluations", sa.Column("request_hash", sa.String(64), nullable=True)
    )
    op.create_index(
        "ix_evaluations_hash_status", "evaluations", ["request_hash", "status"]
    )


def downgrade() -> None:
    op.drop_index("ix_evaluations_hash_status", table_name="evaluations")
    op.drop_column("evaluations", "request_hash")
