
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


def update_workspace(
    session: Session,
    workspace_id: UUID,
    name: str | None = None,
    slug: str | None = None,
    description: str | None = None,
) -> Workspace | None:
    """
    Update workspace details.

    Only the fields provided by the caller are updated.
    Return None if the workspace does not exist.
    """

    try:
        workspace = session.get(Workspace, workspace_id)

        if workspace is None:
            return None

        if name is not None:
            workspace.name = name

        if slug is not None:
            workspace.slug = slug

        if description is not None:
            workspace.description = description

        session.commit()
        session.refresh(workspace)

        return workspace

    except Exception:
        session.rollback()
        raise


def delete_workspace(
    session: Session,
    workspace_id: UUID,
) -> bool:
    """
    Delete a workspace.

    Return True if deleted, or False if not found.
    """

    try:
        workspace = session.get(Workspace, workspace_id)

        if workspace is None:
            return False

        session.delete(workspace)
        session.commit()

        return True

    except Exception:
        session.rollback()
        raise
