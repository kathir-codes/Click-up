"""update task activity enum values

Revision ID: 48be00c69e94
Revises: 38448dc19f8f
Create Date: 2026-11-11 18:01:57.057808

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '48be00c69e94'
down_revision: Union[str, Sequence[str], None] = '38448dc19f8f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("""
        ALTER TYPE task_activity_field ADD VALUE IF NOT EXISTS 'TASK_DELETED';
        ALTER TYPE task_activity_field ADD VALUE IF NOT EXISTS 'TASK_RESTORED';
        ALTER TYPE task_activity_field ADD VALUE IF NOT EXISTS 'DUE_DATE';
        ALTER TYPE task_activity_field ADD VALUE IF NOT EXISTS 'COMMENT_UPDATED';
        ALTER TYPE task_activity_field ADD VALUE IF NOT EXISTS 'COMMENT_DELETED';
        ALTER TYPE task_activity_field ADD VALUE IF NOT EXISTS 'TAG_CREATED';
        ALTER TYPE task_activity_field ADD VALUE IF NOT EXISTS 'TAG_DELETED';
    """)


def downgrade() -> None:
    # PostgreSQL does not directly support removing individual enum values.
    pass
