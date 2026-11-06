from uuid import UUID
from sqlalchemy.orm import Session

from src.models.workspace import Workspace
from src.common.role_permissions import ROLE_PERMISSIONS
from src.common.permissions import Permission
from src.modules.workspace.repositories import workspace_repository as repository
from src.modules.authorization.repository import assign_permissions_to_role
from src.modules.authorization.service import check_workspace_permission


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
        # 1. Create workspace
        workspace = repository.create_workspace_record(
            session=session,
            name=name,
            slug=slug,
            description=description,
            creator_user_id=creator_user_id,
        )

        # 2. Create default roles
        roles = {}

        for role_name, permissions in ROLE_PERMISSIONS.items():

            role = repository.create_workspace_role(
                session=session,
                workspace_id=workspace.workspace_id,
                role_name=role_name,
                creator_user_id=creator_user_id,
            )

            roles[role_name] = role

            # 3. Assign permissions to each role
            assign_permissions_to_role(
                session=session,
                role=role,
                permission_names=permissions,
            )

        # 4. Find Owner role
        owner_role = roles.get("Owner")

        if owner_role is None:
            raise ValueError("Owner role configuration is missing.")

        # 5. Add creator as workspace member
        repository.create_workspace_member(
            session=session,
            workspace_id=workspace.workspace_id,
            user_id=creator_user_id,
            role_id=owner_role.role_id,
        )

        # 6. Commit all operations together
        session.commit()
        session.refresh(workspace)

        return workspace

    except Exception:
        session.rollback()
        raise


# -----------------------------
# UPDATE WORKSPACE
# -----------------------------

def update_workspace(
    session: Session,
    workspace_id: UUID,
    user_id: UUID,
    name: str | None = None,
    slug: str | None = None,
    description: str | None = None,
) -> Workspace | None:

    try:
        # 1. Check permission
        has_permission = check_workspace_permission(
            session=session,
            workspace_id=workspace_id,
            user_id=user_id,
            permission_name=Permission.UPDATE_WORKSPACE,
        )

        if not has_permission:
            raise ValueError(
                "You do not have permission to update this workspace."
            )

        # 2. Find workspace
        workspace = repository.get_workspace(
            session=session,
            workspace_id=workspace_id,
        )

        if workspace is None:
            return None

        # 3. Update workspace
        workspace = repository.update_workspace_record(
            session=session,
            workspace=workspace,
            name=name,
            slug=slug,
            description=description,
        )

        # 4. Commit
        session.commit()
        session.refresh(workspace)

        return workspace

    except Exception:
        session.rollback()
        raise


# -----------------------------
# DELETE WORKSPACE
# -----------------------------

def delete_workspace(
    session: Session,
    workspace_id: UUID,
    user_id: UUID,
) -> bool:

    try:
        # 1. Check permission
        has_permission = check_workspace_permission(
            session=session,
            workspace_id=workspace_id,
            user_id=user_id,
            permission_name=Permission.DELETE_WORKSPACE,
        )

        if not has_permission:
            raise ValueError(
                "You do not have permission to delete this workspace."
            )

        # 2. Find workspace
        workspace = repository.get_workspace(
            session=session,
            workspace_id=workspace_id,
        )

        if workspace is None:
            return False

        # 3. Delete workspace
        repository.delete_workspace_record(
            session=session,
            workspace=workspace,
        )

        # 4. Commit
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

def get_workspace_members(
    session: Session,
    workspace_id: UUID,
):
    return repository.get_workspace_members(
        session=session,
        workspace_id=workspace_id,
    )


# -----------------------------
# REMOVE WORKSPACE MEMBER
# -----------------------------

def remove_workspace_member(
    session: Session,
    workspace_id: UUID,
    requester_user_id: UUID,
    target_user_id: UUID,
) -> bool:

    try:
        # 1. Check REMOVE_MEMBER permission
        has_permission = check_workspace_permission(
            session=session,
            workspace_id=workspace_id,
            user_id=requester_user_id,
            permission_name=Permission.REMOVE_MEMBER,
        )

        if not has_permission:
            raise ValueError(
                "You do not have permission to remove workspace members."
            )

        # 2. Find target member
        membership = repository.get_workspace_member(
            session=session,
            workspace_id=workspace_id,
            user_id=target_user_id,
        )

        if membership is None:
            raise ValueError("Workspace member not found.")

        # 3. Find target member's role
        from src.models.role import Role

        target_role = session.get(Role, membership.role_id)

        if target_role is None:
            raise ValueError("Member role not found.")

        # 4. Prevent removing Owner
        if target_role.role_name == "Owner":
            raise ValueError("Workspace Owner cannot be removed.")

        # 5. Prevent Admin from removing another Admin
        requester_membership = repository.get_workspace_member(
            session=session,
            workspace_id=workspace_id,
            user_id=requester_user_id,
        )

        requester_role = session.get(Role, requester_membership.role_id)

        if (
            requester_role.role_name == "Admin"
            and target_role.role_name != "Member"
        ):
            raise ValueError(
                "Admin can remove Members only."
            )

        # 6. Delete workspace membership
        repository.delete_workspace_member(
            session=session,
            membership=membership,
        )

        # 7. Commit
        session.commit()

        return True

    except Exception:
        session.rollback()
        raise


# -----------------------------
# RESTORE WORKSPACE
# -----------------------------

def restore_workspace(
    session: Session,
    workspace_id: UUID,
    user_id: UUID,
) -> bool:

    try:
        # 1. Check permission
        has_permission = check_workspace_permission(
            session=session,
            workspace_id=workspace_id,
            user_id=user_id,
            permission_name=Permission.DELETE_WORKSPACE,
        )

        if not has_permission:
            raise ValueError(
                "You do not have permission to restore this workspace."
            )

        # 2. Find workspace, including deleted records
        workspace = session.get(Workspace, workspace_id)

        if workspace is None or workspace.deleted_at is None:
            return False

        # 3. Restore workspace
        repository.restore_workspace_record(
            session=session,
            workspace=workspace,
        )

        # 4. Commit
        session.commit()

        return True

    except Exception:
        session.rollback()
        raise