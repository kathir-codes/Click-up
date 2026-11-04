
from uuid import UUID
from sqlalchemy.orm import Session

from src.models.task import Task
from src.modules.task import repository
from src.modules.authorization.service import check_workspace_permission


# -----------------------------
# GET WORKSPACE TASKS
# -----------------------------

def get_workspace_tasks(
    session: Session,
    workspace_id: UUID,
    user_id: UUID,
) -> list[Task]:

    # 1. Check VIEW_TASK permission
    has_permission = check_workspace_permission(
        session=session,
        workspace_id=workspace_id,
        user_id=user_id,
        permission_name="VIEW_TASK",
    )

    if not has_permission:
        raise ValueError(
            "You do not have permission to view workspace tasks."
        )

    # 2. Get workspace tasks
    return repository.get_tasks_by_workspace(
        session=session,
        workspace_id=workspace_id,
    )
