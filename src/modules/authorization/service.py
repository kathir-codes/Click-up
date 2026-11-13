from src.modules.authorization.repository import user_has_workspace_permission


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
