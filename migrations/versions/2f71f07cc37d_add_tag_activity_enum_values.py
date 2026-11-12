"""add tag activity enum values

Revision ID: 2f71f07cc37d
Revises: 48be00c69e94
Create Date: 2026-11-12 11:20:52.740339

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2f71f07cc37d'
down_revision: Union[str, Sequence[str], None] = '48be00c69e94'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "ALTER TYPE task_activity_field "
        "ADD VALUE IF NOT EXISTS 'TAG_ADDED'"
    )
    op.execute(
        "ALTER TYPE task_activity_field "
        "ADD VALUE IF NOT EXISTS 'TAG_REMOVED'"
    )


def downgrade() -> None:
    pass