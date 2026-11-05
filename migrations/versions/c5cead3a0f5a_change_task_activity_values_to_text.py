"""change task activity values to text

Revision ID: c5cead3a0f5a
Revises: cedbc1280fae
Create Date: 2026-11-05 16:04:14.715723

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'c5cead3a0f5a'
down_revision: Union[str, Sequence[str], None] = 'cedbc1280fae'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "task_activity",
        "old_value",
        existing_type=sa.VARCHAR(length=100),
        type_=sa.Text(),
        existing_nullable=True,
    )

    op.alter_column(
        "task_activity",
        "new_value",
        existing_type=sa.VARCHAR(length=100),
        type_=sa.Text(),
        existing_nullable=True,
    )


def downgrade() -> None:
    op.alter_column(
        "task_activity",
        "new_value",
        existing_type=sa.Text(),
        type_=sa.VARCHAR(length=100),
        existing_nullable=True,
    )

    op.alter_column(
        "task_activity",
        "old_value",
        existing_type=sa.Text(),
        type_=sa.VARCHAR(length=100),
        existing_nullable=True,
    )

