
"""seed permission data

Revision ID: 85cc397ddde0
Revises: 313686894ea5
"""

from typing import Sequence, Union
from uuid import uuid4

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "85cc397ddde0"
down_revision: Union[str, Sequence[str], None] = "313686894ea5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


PERMISSIONS = [
    ("CREATE_WORKSPACE", "Create a workspace"),
    ("UPDATE_WORKSPACE", "Update a workspace"),
    ("DELETE_WORKSPACE", "Delete a workspace"),
    ("INVITE_MEMBER", "Invite workspace members"),
    ("VIEW_INVITATIONS", "View workspace invitations"),
    ("VIEW_WORKSPACE_MEMBERS", "View workspace members"),
    ("CANCEL_INVITATION", "Cancel an invitation"),
    ("RESEND_INVITATION", "Resend an invitation"),
    ("REMOVE_MEMBER", "Remove a workspace member"),
    ("VIEW_ROLES", "View workspace roles"),
    ("CREATE_ROLE", "Create a custom role"),
    ("UPDATE_ROLE", "Update a role"),
    ("DELETE_ROLE", "Delete a custom role"),
    ("MANAGE_ROLE_PERMISSIONS", "Assign permissions to roles"),
    ("CREATE_TASK", "Create a task"),
    ("VIEW_TASK", "View task details"),
    ("UPDATE_TASK", "Update a task"),
    ("DELETE_TASK", "Delete a task"),
    ("ASSIGN_TASK", "Assign a task"),
    ("UPDATE_TASK_STATUS", "Update task status"),
    ("UPDATE_TASK_PRIORITY", "Update task priority"),
    ("CREATE_TAG", "Create a tag"),
    ("UPDATE_TAG", "Update a tag"),
    ("DELETE_TAG", "Delete a tag"),
    ("MANAGE_TASK_TAGS", "Add or remove task tags"),
    ("ADD_COMMENT", "Add a comment"),
    ("UPDATE_COMMENT", "Update a comment"),
    ("DELETE_COMMENT", "Delete a comment"),
    ("VIEW_TASK_ACTIVITY", "View task activity history"),
]



def upgrade() -> None:
    connection = op.get_bind()

    for permission_name, description in PERMISSIONS:
        connection.execute(
            sa.text("""
                INSERT INTO permissions (
                    permission_id,
                    permission_name,
                    description
                )
                VALUES (
                    gen_random_uuid(),
                    :permission_name,
                    :description
                )
                ON CONFLICT (permission_name)
                DO UPDATE SET
                    description = EXCLUDED.description
            """),
            {
                "permission_name": permission_name,
                "description": description,
            },
        )


def downgrade() -> None:
    # Keep permission records to protect existing role assignments.
    pass
