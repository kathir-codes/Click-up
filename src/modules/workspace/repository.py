from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from src.models.workspace import Workspace, WorkspaceMember
from src.models.role import Role


# -----------------------------
# WORKSPACE OPERATIONS
# -----------------------------

def create_workspace_record(
    session: Session,
    name: str,
    slug: str,
    description: str | None,
    creator_user_id: UUID,
) -> Workspace:
    workspace = Workspace(
        name=name,
        slug=slug,
        description=description,
        created_by=creator_user_id,
    )

    session.add(workspace)
    session.flush()

    return workspace


def get_workspace(
    session: Session,
    workspace_id: UUID,
) -> Workspace | None:

    return session.get(Workspace, workspace_id)


def update_workspace_record(
    session: Session,
    workspace: Workspace,
    name: str | None = None,
    slug: str | None = None,
    description: str | None = None,
) -> Workspace:

    if name is not None:
        workspace.name = name

    if slug is not None:
        workspace.slug = slug

    if description is not None:
        workspace.description = description

    session.flush()

    return workspace


def delete_workspace_record(
    session: Session,
    workspace: Workspace,
) -> None:

    session.delete(workspace)
    session.flush()


# -----------------------------
# ROLE OPERATIONS
# -----------------------------

def create_workspace_role(
    session: Session,
    workspace_id: UUID,
    role_name: str,
    creator_user_id: UUID,
) -> Role:

    role = Role(
        workspace_id=workspace_id,
        role_name=role_name,
        is_system_role=True,
        created_by=creator_user_id,
    )

    session.add(role)
    session.flush()

    return role


def get_workspace_role(
    session: Session,
    workspace_id: UUID,
    role_name: str,
) -> Role | None:

    statement = select(Role).where(
        Role.workspace_id == workspace_id,
        Role.role_name == role_name,
    )

    return session.scalar(statement)


# -----------------------------
# WORKSPACE MEMBER OPERATIONS
# -----------------------------

def create_workspace_member(
    session: Session,
    workspace_id: UUID,
    user_id: UUID,
    role_id: UUID,
) -> WorkspaceMember:

    membership = WorkspaceMember(
        workspace_id=workspace_id,
        user_id=user_id,
        role_id=role_id,
    )

    session.add(membership)
    session.flush()

    return membership


# -----------------------------
# WORKSPACE QUERY OPERATIONS
# -----------------------------

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