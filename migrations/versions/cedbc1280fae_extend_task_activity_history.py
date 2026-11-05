"""extend task activity history

Revision ID: cedbc1280fae
Revises: e107e29b3223
Create Date: 2026-11-05 16:01:38.281484

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cedbc1280fae'
down_revision: Union[str, Sequence[str], None] = 'e107e29b3223'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    values = [
        "TASK_CREATED",
        "TITLE",
        "DESCRIPTION",
        "ASSIGNEE",
        "TAG_ADDED",
        "TAG_REMOVED",
        "COMMENT_ADDED",
    ]

    for value in values:
        op.execute(
            f"ALTER TYPE task_activity_field "
            f"ADD VALUE IF NOT EXISTS '{value}'"
        )


def downgrade() -> None:
    pass