
from uuid import UUID

from sqlalchemy.orm import Session

from src.common.permissions import Permission
from src.models.task import TaskActivity, TaskActivityField
from src.modules.authorization.decorators import require_workspace_permission
from src.modules.task.repositories import activity_repository, task_repository

# -----------------------------
# CREATE TASK ACTIVITY
# -----------------------------

def create_task_activity(
    session: Session,
    task_id: UUID,
    user_id: UUID,
    field: TaskActivityField,
    old_value: str | None,
    new_value: str | None,
) -> TaskActivity:

    return activity_repository.create_task_activity(
        session=session,
        task_id=task_id,
        user_id=user_id,
        field=field,
        old_value=old_value,
        new_value=new_value,
    )


# -----------------------------
# GET TASK ACTIVITIES
# -----------------------------

@require_workspace_permission(Permission.VIEW_TASK_ACTIVITY)
def get_task_activities(
    session: Session,
    task_id: UUID,
    workspace_id: UUID,
    user_id: UUID,
) -> list[TaskActivity]:

    # Verify task belongs to workspace
    task = task_repository.get_task_by_id(
        session=session,
        task_id=task_id,
        workspace_id=workspace_id,
    )

    if task is None:
        raise ValueError("Task not found.")

    return activity_repository.get_task_activities(
        session=session,
        task_id=task_id,
    )
