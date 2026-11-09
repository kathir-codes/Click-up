
from uuid import UUID

from sqlalchemy.orm import Session

from src.common.permissions import Permission
from src.models.task import Task
from src.modules.authorization.decorators import require_workspace_permission
from src.modules.task.repositories import task_repository
from src.modules.workspace.services.workspace_service import check_workspace_is_active


# -----------------------------
# GET TRASH TASKS
# -----------------------------

@require_workspace_permission(Permission.VIEW_TASK)
def get_deleted_tasks(
    session: Session,
    workspace_id: UUID,
    user_id: UUID,
) -> list[Task]:

    # Check whether workspace is active
    check_workspace_is_active(
        session=session,
        workspace_id=workspace_id,
    )

    return task_repository.get_deleted_tasks_by_workspace(
        session=session,
        workspace_id=workspace_id,
    )


# -----------------------------
# RESTORE TASK
# -----------------------------

@require_workspace_permission(Permission.DELETE_TASK)
def restore_task(
    session: Session,
    task_id: UUID,
    workspace_id: UUID,
    user_id: UUID,
) -> Task:

    try:
        # Check whether workspace is active
        check_workspace_is_active(
            session=session,
            workspace_id=workspace_id,
        )

        # Find the task in Trash
        deleted_tasks = task_repository.get_deleted_tasks_by_workspace(
            session=session,
            workspace_id=workspace_id,
        )

        task = next(
            (item for item in deleted_tasks if item.task_id == task_id),
            None,
        )

        if task is None:
            raise ValueError("Deleted task not found.")

        task_repository.restore_task_record(
            session=session,
            task=task,
        )

        session.commit()
        session.refresh(task)

        return task

    except Exception:
        session.rollback()
        raise
