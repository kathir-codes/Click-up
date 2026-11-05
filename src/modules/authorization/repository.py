
from src.models.role import Role, Permission, RolePermission
from src.models.workspace import WorkspaceMember


def assign_permissions_to_role(session, role, permission_names):

    # Convert Enum values into strings
    permission_names = {
        permission.value if hasattr(permission, "value") else permission
        for permission in permission_names
    }

    # Find permission records in the database
    permissions = (
        session.query(Permission)
        .filter(Permission.permission_name.in_(permission_names))
        .all()
    )

    # Check whether every requested permission exists
    found_names = {permission.permission_name for permission in permissions}
    missing_names = permission_names - found_names

    if missing_names:
        raise ValueError(
            f"Permissions not found in database: {sorted(missing_names)}"
        )

    # Find permissions already assigned to this role
    existing_permission_ids = {
        permission_id
        for (permission_id,) in (
            session.query(RolePermission.permission_id)
            .filter(RolePermission.role_id == role.role_id)
            .all()
        )
    }

    # Assign only permissions that are not already assigned
    for permission in permissions:
        if permission.permission_id not in existing_permission_ids:
            role_permission = RolePermission(
                role_id=role.role_id,
                permission_id=permission.permission_id,
            )
            session.add(role_permission)

def user_has_workspace_permission(
    session,
    workspace_id,
    user_id,
    permission_name,
):
    permission_name = (
        permission_name.value
        if hasattr(permission_name, "value")
        else permission_name
    )

    return (
        session.query(Permission)
        .join(
            RolePermission,
            RolePermission.permission_id == Permission.permission_id,
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
            Permission.permission_name == permission_name,
        )
        .first()
        is not None
    )