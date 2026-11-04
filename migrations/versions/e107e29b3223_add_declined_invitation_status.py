"""add declined invitation status

Revision ID: e107e29b3223
Revises: b13cfa2088c1
Create Date: 2026-11-04 15:21:29.773364

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'e107e29b3223'
down_revision: Union[str, Sequence[str], None] = 'b13cfa2088c1'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "ALTER TYPE invitation_status ADD VALUE IF NOT EXISTS 'DECLINED'"
    )


def downgrade() -> None:
    pass
