
from uuid import UUID

from sqlalchemy.orm import Session

from src.models.workspace import Workspace, WorkspaceMember
from src.models.role import Role
from src.authorization.role_permissions import ROLE_PERMISSIONS
from src.database.role_permission_operations import (
    assign_permissions_to_role,
)


def create_workspace(
    session: Session,
    name: str,
    slug: str,
    description: str | None,
    creator_user_id: UUID,
) -> Workspace:
    """
    Create a workspace, its system roles, role permissions,
    and the creator's Owner membership in one transaction.
    """

    try:
        # 1. Create the workspace.
        workspace = Workspace(
            name=name,
            slug=slug,
            description=description,
            created_by=creator_user_id,
        )
        session.add(workspace)
        session.flush()

        # 2. Create Owner, Admin, and Member roles.
        roles = {}

        for role_name in ROLE_PERMISSIONS:
            role = Role(
                workspace_id=workspace.workspace_id,
                role_name=role_name,
                is_system_role=True,
                created_by=creator_user_id,
            )
            session.add(role)
            session.flush()

            roles[role_name] = role

            # 3. Assign permissions to this role.
            assign_permissions_to_role(
                session=session,
                role=role,
                permission_names=ROLE_PERMISSIONS[role_name],
            )

        # 4. Add the creator as a workspace Owner.
        membership = WorkspaceMember(
            workspace_id=workspace.workspace_id,
            user_id=creator_user_id,
            role_id=roles["Owner"].role_id,
        )
        session.add(membership)

        # 5. Commit all changes together.
        session.commit()

        return workspace

    except Exception:
        session.rollback()
        raise
