from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session
from datetime import datetime, timezone
from src.models.workspace import Workspace, WorkspaceMember
from src.models.role import Role
from src.models.user import User, UserProfile


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

    statement = select(Workspace).where(
        Workspace.workspace_id == workspace_id,
        Workspace.deleted_at.is_(None),
    )

    return session.scalar(statement)

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

    workspace.deleted_at = datetime.now(timezone.utc)

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


def get_role_by_name(
    session: Session,
    workspace_id: UUID,
    role_name: str,
) -> Role | None:

    return (
        session.query(Role)
        .filter(
            Role.workspace_id == workspace_id,
            Role.role_name == role_name,
        )
        .first()
    )


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


def get_workspace_member(
    session: Session,
    workspace_id: UUID,
    user_id: UUID,
) -> WorkspaceMember | None:

    statement = select(WorkspaceMember).where(
        WorkspaceMember.workspace_id == workspace_id,
        WorkspaceMember.user_id == user_id,
    )

    return session.scalar(statement)


def get_workspace_members(
    session: Session,
    workspace_id: UUID,
):

    statement = (
        select(
            WorkspaceMember,
            UserProfile,
            User.email,
            Role.role_name,
        )
        .join(
            User,
            WorkspaceMember.user_id == User.user_id,
        )
        .join(
            UserProfile,
            User.user_id == UserProfile.user_id,
        )
        .join(
            Role,
            WorkspaceMember.role_id == Role.role_id,
        )
        .where(
            WorkspaceMember.workspace_id == workspace_id,
        )
        .order_by(
            WorkspaceMember.joined_at.asc(),
        )
    )

    return session.execute(statement).all()


def delete_workspace_member(
    session: Session,
    membership: WorkspaceMember,
) -> None:

    session.delete(membership)
    session.flush()


# -----------------------------
# WORKSPACE QUERY OPERATIONS
# -----------------------------
# Get all active workspaces that a particular user belongs to.
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
        .where(
            WorkspaceMember.user_id == user_id,
            Workspace.deleted_at.is_(None),
        )
        .order_by(
            Workspace.created_at.desc(),
        )
    )

    return list(session.scalars(statement).all())

# -----------------------------
# GET USER WORKSPACE
# -----------------------------
#Get one specific workspace that a particular user belongs to.

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
            Workspace.deleted_at.is_(None),
        )
    )

    return session.scalar(statement)


# -----------------------------
# RESTORE WORKSPACE
# -----------------------------

def restore_workspace_record(
    session: Session,
    workspace: Workspace,
) -> Workspace:

    workspace.deleted_at = None

    session.flush()

    return workspace