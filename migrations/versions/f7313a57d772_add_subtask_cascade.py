"""add subtask cascade

Revision ID: f7313a57d772
Revises: c5cead3a0f5a
Create Date: 2026-11-06 12:46:40.087105
"""

from typing import Sequence, Union

from alembic import op


# revision identifiers
revision: str = "f7313a57d772"
down_revision: Union[str, Sequence[str], None] = "c5cead3a0f5a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    # Remove existing composite foreign key
    op.drop_constraint(
        "fk_task_parent_same_workspace",
        "tasks",
        type_="foreignkey",
    )

    # Recreate it with ON DELETE CASCADE
    op.create_foreign_key(
        "fk_task_parent_same_workspace",
        "tasks",
        "tasks",
        ["workspace_id", "parent_task_id"],
        ["workspace_id", "task_id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:

    # Remove the CASCADE constraint
    op.drop_constraint(
        "fk_task_parent_same_workspace",
        "tasks",
        type_="foreignkey",
    )

    # Restore the original constraint
    op.create_foreign_key(
        "fk_task_parent_same_workspace",
        "tasks",
        "tasks",
        ["workspace_id", "parent_task_id"],
        ["workspace_id", "task_id"],
    )