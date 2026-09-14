"""New value in status enum

Revision ID: 7704e020cc22
Revises: 26feb7e6d397
Create Date: 2026-09-14 08:16:56.745265

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7704e020cc22'
down_revision: Union[str, Sequence[str], None] = '26feb7e6d397'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("ALTER TYPE upload_status ADD VALUE IF NOT EXISTS 'expired'")


def downgrade() -> None:
    """Downgrade schema."""
    # Postgres doesn't support removing a value from an enum type without
    # recreating it; not worth the risk/complexity for an additive status.
    pass
