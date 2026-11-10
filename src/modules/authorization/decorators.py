
from functools import wraps
from inspect import signature

from src.common.permissions import Permission
from src.modules.authorization.service import check_workspace_permission


def require_workspace_permission(permission: Permission):
    """Validate workspace permission before executing a service function."""

    def decorator(func):
        function_signature = signature(func)

        @wraps(func)
        def wrapper(*args, **kwargs):
            bound_arguments = function_signature.bind(*args, **kwargs)

            session = bound_arguments.arguments["session"]
            workspace_id = bound_arguments.arguments["workspace_id"]
            user_id = bound_arguments.arguments["user_id"]

            has_permission = check_workspace_permission(
                session=session,
                workspace_id=workspace_id,
                user_id=user_id,
                permission_name=permission,
            )

            if not has_permission:
                raise ValueError(
                    f"You do not have permission: {permission.name}."
                )

            return func(*args, **kwargs)

        return wrapper

    return decorator
