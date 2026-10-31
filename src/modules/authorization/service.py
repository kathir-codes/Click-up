from src.modules.authorization.repository import (
    assign_permissions_to_role,
    user_has_workspace_permission,
)


def assign_role_permissions(session, role, permission_names):
    return assign_permissions_to_role(
        session=session,
        role=role,
        permission_names=permission_names,
    )


def check_workspace_permission(
    session,
    workspace_id,
    user_id,
    permission_name,
):
    return user_has_workspace_permission(
        session=session,
        workspace_id=workspace_id,
        user_id=user_id,
        permission_name=permission_name,
    )