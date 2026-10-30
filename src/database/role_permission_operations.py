from src.models.role import Role, Permission, RolePermission


def assign_permissions_to_role(session, role, permission_names):
    """
    Assign permissions to a role.

    Args:
        session: Active SQLAlchemy database session.
        role: The Role database object.
        permission_names: Set of permission names to assign.
    """

    # Find permission records in the database.
    permissions = (
        session.query(Permission)
        .filter(Permission.permission_name.in_(permission_names))
        .all()
    )

    # Check whether every requested permission exists.
    found_names = {permission.permission_name for permission in permissions}
    missing_names = set(permission_names) - found_names

    if missing_names:
        raise ValueError(
            f"Permissions not found in database: {sorted(missing_names)}"
        )

    # Find permissions already assigned to this role.
    existing_permission_ids = {
        permission_id
        for (permission_id,) in (
            session.query(RolePermission.permission_id)
            .filter(RolePermission.role_id == role.role_id)
            .all()
        )
    }

    # Assign only permissions that are not already assigned.
    for permission in permissions:
        if permission.permission_id not in existing_permission_ids:
            role_permission = RolePermission(
                role_id=role.role_id,
                permission_id=permission.permission_id,
            )
            session.add(role_permission)