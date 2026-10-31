from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.models.workspace import Workspace, WorkspaceMember
from src.models.role import Role
from src.common.role_permissions import ROLE_PERMISSIONS
from src.modules.authorization.repository import assign_permissions_to_role

def create_workspace(
    session: Session,
    name: str,
    slug: str,
    description: str | None,
    creator_user_id: UUID,
) -> Workspace:
    try:
        workspace = Workspace(
            name=name,
            slug=slug,
            description=description,
            created_by=creator_user_id,
        )
        session.add(workspace)
        session.flush()

        roles = {}

        for role_name, permissions in ROLE_PERMISSIONS.items():
            role = Role(
                workspace_id=workspace.workspace_id,
                role_name=role_name,
                is_system_role=True,
                created_by=creator_user_id,
            )
            session.add(role)
            session.flush()

            roles[role_name] = role

            assign_permissions_to_role(
                session=session,
                role=role,
                permission_names=permissions,
            )

        membership = WorkspaceMember(
            workspace_id=workspace.workspace_id,
            user_id=creator_user_id,
            role_id=roles["Owner"].role_id,
        )
        session.add(membership)

        session.commit()
        session.refresh(workspace)

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


def get_user_workspaces(
    session: Session,
    user_id: UUID,
) -> list[Workspace]:
    statement = (
        select(Workspace)
        .join(
            WorkspaceMember,
            Workspace.workspace_id == WorkspaceMember.workspace_id,
        )
        .where(WorkspaceMember.user_id == user_id)
        .order_by(Workspace.created_at.desc())
    )

    return list(session.scalars(statement).all())


def get_user_workspace(
    session: Session,
    workspace_id: UUID,
    user_id: UUID,
) -> Workspace | None:
    statement = (
        select(Workspace)
        .join(
            WorkspaceMember,
            Workspace.workspace_id == WorkspaceMember.workspace_id,
        )
        .where(
            Workspace.workspace_id == workspace_id,
            WorkspaceMember.user_id == user_id,
        )
    )

    return session.scalar(statement)