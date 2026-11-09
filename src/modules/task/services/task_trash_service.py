from uuid import UUID

from sqlalchemy.orm import Session

from src.common.permissions import Permission
from src.models.task import Task
from src.modules.task.repositories import task_repository
from src.modules.authorization.service import check_workspace_permission
from src.modules.workspace.services.workspace_service import (
    check_workspace_is_active,
)


# -----------------------------
# GET TRASH TASKS
# -----------------------------

def get_deleted_tasks(
    session: Session,
    workspace_id: UUID,
    user_id: UUID,
) -> list[Task]:

    # -----------------------------
    # CHECK WHETHER WORKSPACE IS ACTIVE
    # -----------------------------
    check_workspace_is_active(
        session=session,
        workspace_id=workspace_id,
    )

    has_permission = check_workspace_permission(
        session=session,
        workspace_id=workspace_id,
        user_id=user_id,
        permission_name=Permission.VIEW_TASK,
    )

    if not has_permission:
        raise ValueError("You do not have permission to view deleted tasks.")

    return task_repository.get_deleted_tasks_by_workspace(
        session=session,
        workspace_id=workspace_id,
    )



# -----------------------------
# RESTORE TASK
# -----------------------------

def restore_task(
    session: Session,
    task_id: UUID,
    workspace_id: UUID,
    user_id: UUID,
) -> Task:

    try:
        # -----------------------------
        # CHECK WHETHER WORKSPACE IS ACTIVE
        # -----------------------------
        check_workspace_is_active(
            session=session,
            workspace_id=workspace_id,
        )

        has_permission = check_workspace_permission(
            session=session,
            workspace_id=workspace_id,
            user_id=user_id,
            permission_name=Permission.DELETE_TASK,
        )

        if not has_permission:
            raise ValueError("You do not have permission to restore tasks.")

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