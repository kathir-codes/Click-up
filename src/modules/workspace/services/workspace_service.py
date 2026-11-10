
from uuid import UUID

from sqlalchemy.orm import Session

from src.common.permissions import Permission
from src.common.role_permissions import ROLE_PERMISSIONS
from src.models.role import Role
from src.models.workspace import Workspace
from src.modules.authorization.decorators import require_workspace_permission
from src.modules.authorization.repository import assign_permissions_to_role
from src.modules.workspace.repositories import workspace_repository as repository

# -----------------------------
# CREATE WORKSPACE
# -----------------------------

def create_workspace(
    session: Session,
    name: str,
    slug: str,
    description: str | None,
    creator_user_id: UUID,
) -> Workspace:
    try:
        # Check whether the slug is already used.
        existing_workspace = repository.get_workspace_by_slug(
            session=session,
            slug=slug,
        )

        if existing_workspace:
            raise ValueError(
                "A workspace with this slug already exists."
            )

        workspace = repository.create_workspace_record(
            session=session,
            name=name,
            slug=slug,
            description=description,
            creator_user_id=creator_user_id,
        )

        roles = {}

        for role_name, permissions in ROLE_PERMISSIONS.items():
            role = repository.create_workspace_role(
                session=session,
                workspace_id=workspace.workspace_id,
                role_name=role_name,
                creator_user_id=creator_user_id,
            )

            roles[role_name] = role

            assign_permissions_to_role(
                session=session,
                role=role,
                permission_names=permissions,
            )

        owner_role = roles.get("Owner")

        if owner_role is None:
            raise ValueError("Owner role configuration is missing.")

        repository.create_workspace_member(
            session=session,
            workspace_id=workspace.workspace_id,
            user_id=creator_user_id,
            role_id=owner_role.role_id,
        )

        session.commit()
        session.refresh(workspace)

        return workspace

    except Exception:
        session.rollback()
        raise


# -----------------------------
# UPDATE WORKSPACE
# -----------------------------

@require_workspace_permission(Permission.UPDATE_WORKSPACE)
def update_workspace(
    session: Session,
    workspace_id: UUID,
    user_id: UUID,
    name: str | None = None,
    slug: str | None = None,
    description: str | None = None,
) -> Workspace | None:

    try:
        workspace = repository.get_workspace(
            session=session,
            workspace_id=workspace_id,
        )

        if workspace is None:
            return None

        workspace = repository.update_workspace_record(
            session=session,
            workspace=workspace,
            name=name,
            slug=slug,
            description=description,
        )

        session.commit()
        session.refresh(workspace)

        return workspace

    except Exception:
        session.rollback()
        raise


# -----------------------------
# DELETE WORKSPACE
# -----------------------------

@require_workspace_permission(Permission.DELETE_WORKSPACE)
def delete_workspace(
    session: Session,
    workspace_id: UUID,
    user_id: UUID,
) -> bool:

    try:
        workspace = repository.get_workspace(
            session=session,
            workspace_id=workspace_id,
        )

        if workspace is None:
            return False

        repository.delete_workspace_record(
            session=session,
            workspace=workspace,
        )

        session.commit()

        return True

    except Exception:
        session.rollback()
        raise


# -----------------------------
# GET USER WORKSPACES
# -----------------------------

def get_user_workspaces(
    session: Session,
    user_id: UUID,
) -> list[Workspace]:

    return repository.get_user_workspaces(
        session=session,
        user_id=user_id,
    )


# -----------------------------
# GET SINGLE USER WORKSPACE
# -----------------------------

def get_user_workspace(
    session: Session,
    workspace_id: UUID,
    user_id: UUID,
) -> Workspace | None:

    return repository.get_user_workspace(
        session=session,
        workspace_id=workspace_id,
        user_id=user_id,
    )


# -----------------------------
# GET WORKSPACE MEMBERS
# -----------------------------

@require_workspace_permission(Permission.VIEW_WORKSPACE_MEMBERS)
def get_workspace_members(
    session: Session,
    workspace_id: UUID,
    user_id: UUID,
):
    return repository.get_workspace_members(
        session=session,
        workspace_id=workspace_id,
    )


# -----------------------------
# REMOVE WORKSPACE MEMBER
# -----------------------------

@require_workspace_permission(Permission.REMOVE_MEMBER)
def remove_workspace_member(
    session: Session,
    workspace_id: UUID,
    user_id: UUID,
    target_user_id: UUID,
) -> bool:

    try:
        membership = repository.get_workspace_member(
            session=session,
            workspace_id=workspace_id,
            user_id=target_user_id,
        )

        if membership is None:
            raise ValueError("Workspace member not found.")

        target_role = session.get(Role, membership.role_id)

        if target_role is None:
            raise ValueError("Member role not found.")

        if target_role.role_name == "Owner":
            raise ValueError("Workspace Owner cannot be removed.")

        requester_membership = repository.get_workspace_member(
            session=session,
            workspace_id=workspace_id,
            user_id=user_id,
        )

        if requester_membership is None:
            raise ValueError("Requester is not a workspace member.")

        requester_role = session.get(Role, requester_membership.role_id)

        if requester_role is None:
            raise ValueError("Requester role not found.")

        if (
            requester_role.role_name == "Admin"
            and target_role.role_name != "Member"
        ):
            raise ValueError("Admin can remove Members only.")

        repository.delete_workspace_member(
            session=session,
            membership=membership,
        )

        session.commit()

        return True

    except Exception:
        session.rollback()
        raise


# -----------------------------
# RESTORE WORKSPACE
# -----------------------------

@require_workspace_permission(Permission.DELETE_WORKSPACE)
def restore_workspace(
    session: Session,
    workspace_id: UUID,
    user_id: UUID,
) -> bool:

    try:
        workspace = session.get(Workspace, workspace_id)

        if workspace is None or workspace.deleted_at is None:
            return False

        repository.restore_workspace_record(
            session=session,
            workspace=workspace,
        )

        session.commit()

        return True

    except Exception:
        session.rollback()
        raise


# -----------------------------
# CHECK WHETHER WORKSPACE IS ACTIVE
# -----------------------------

def check_workspace_is_active(
    session: Session,
    workspace_id: UUID,
):
    workspace = repository.get_workspace(
        session=session,
        workspace_id=workspace_id,
    )

    if workspace is None:
        raise ValueError("Workspace not found or has been deleted.")

    return workspace
