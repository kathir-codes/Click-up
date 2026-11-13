from src.common.permissions import Permission as PermissionEnum
from src.models.role import Permission as PermissionModel
from src.models.role import Role, RolePermission
from src.models.workspace import WorkspaceMember

def user_has_workspace_permission(
    session,
    workspace_id,
    user_id,
    permission_name,
):
    """
    Check whether a user has a particular permission
    in a particular workspace.
    """

    # Convert Enum member into its database identifier
    if isinstance(permission_name, PermissionEnum):
        permission_name = permission_name.name

    return (
        session.query(PermissionModel)
        .join(
            RolePermission,
            RolePermission.permission_id == PermissionModel.permission_id,
        )
        .join(
            Role,
            Role.role_id == RolePermission.role_id,
        )
        .join(
            WorkspaceMember,
            WorkspaceMember.role_id == Role.role_id,
        )
        .filter(
            WorkspaceMember.workspace_id == workspace_id,
            WorkspaceMember.user_id == user_id,
            PermissionModel.permission_name == permission_name,
        )
        .first()
        is not None
    )