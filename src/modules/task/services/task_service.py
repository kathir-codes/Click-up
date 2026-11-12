
from datetime import datetime
from uuid import UUID

from sqlalchemy.orm import Session

from src.common.permissions import Permission
from src.models.task import Task, TaskActivityField, TaskPriority, TaskStatus
from src.modules.authorization.decorators import require_workspace_permission
from src.modules.task.repositories import task_repository
from src.modules.task.services.activity_service import create_task_activity
from src.modules.workspace.services.workspace_service import check_workspace_is_active
from src.modules.task.decorators.activity_decorators import track_activity
# -----------------------------
# CREATE TASK
# -----------------------------

@require_workspace_permission(Permission.CREATE_TASK)
@track_activity(
    field=TaskActivityField.TASK_CREATED,
    new_value_attr="title",
)
def create_task(
    session: Session,
    workspace_id: UUID,
    user_id: UUID,
    title: str,
    description: str | None = None,
    status: TaskStatus = TaskStatus.TODO,
    priority: TaskPriority = TaskPriority.MEDIUM,
    assignee_id: UUID | None = None,
    due_date: datetime | None = None,
) -> Task:

    check_workspace_is_active(
        session=session,
        workspace_id=workspace_id,
    )

    # Validate assignee
    if assignee_id is not None:
        from src.models.workspace import WorkspaceMember

        member = (
            session.query(WorkspaceMember)
            .filter(
                WorkspaceMember.workspace_id == workspace_id,
                WorkspaceMember.user_id == assignee_id,
            )
            .first()
        )

        if member is None:
            raise ValueError("Assignee is not a member of this workspace.")

    task = task_repository.create_task_record(
        session=session,
        workspace_id=workspace_id,
        title=title,
        description=description,
        created_by=user_id,
        status=status,
        priority=priority,
        assignee_id=assignee_id,
        due_date=due_date,
    )

    return task


# -----------------------------
# GET WORKSPACE TASKS
# -----------------------------

@require_workspace_permission(Permission.VIEW_TASK)
def get_workspace_tasks(
    session: Session,
    workspace_id: UUID,
    user_id: UUID,
) -> list[Task]:

    check_workspace_is_active(
        session=session,
        workspace_id=workspace_id,
    )

    return task_repository.get_tasks_by_workspace(
        session=session,
        workspace_id=workspace_id,
    )


# -----------------------------
# GET TASK BY ID
# -----------------------------

@require_workspace_permission(Permission.VIEW_TASK)
def get_task_by_id(
    session: Session,
    task_id: UUID,
    workspace_id: UUID,
    user_id: UUID,
) -> Task:

    check_workspace_is_active(
        session=session,
        workspace_id=workspace_id,
    )

    task = task_repository.get_task_by_id(
        session=session,
        task_id=task_id,
        workspace_id=workspace_id,
    )

    if task is None:
        raise ValueError("Task not found.")

    return task


# -----------------------------
# UPDATE TASK
# -----------------------------


@require_workspace_permission(Permission.UPDATE_TASK)
@track_activity(
    tracked_fields={
        "title": TaskActivityField.TITLE,
        "description": TaskActivityField.DESCRIPTION,
        "status": TaskActivityField.STATUS,
        "priority": TaskActivityField.PRIORITY,
        "due_date": TaskActivityField.DUE_DATE,
    },
    loader=task_repository.get_task_by_id,
    loader_args=("task_id", "workspace_id"),
)


def update_task(
    session: Session,
    task_id: UUID,
    workspace_id: UUID,
    user_id: UUID,
    title: str | None = None,
    description: str | None = None,
    due_date: datetime | None = None,
    status: TaskStatus | None = None,
    priority: TaskPriority | None = None,
) -> Task:

    check_workspace_is_active(
        session=session,
        workspace_id=workspace_id,
    )

    task = task_repository.get_task_by_id(
        session=session,
        task_id=task_id,
        workspace_id=workspace_id,
    )

    if task is None:
        raise ValueError("Task not found.")

    task = task_repository.update_task_record(
        session=session,
        task=task,
        title=title,
        description=description,
        due_date=due_date,
        status=status,
        priority=priority,
    )

    return task



# -----------------------------
# DELETE TASK
# -----------------------------

@require_workspace_permission(Permission.DELETE_TASK)
@track_activity(
    field=TaskActivityField.TASK_DELETED,
)
def delete_task(
    session: Session,
    task_id: UUID,
    workspace_id: UUID,
    user_id: UUID,
) -> bool:

    check_workspace_is_active(
        session=session,
        workspace_id=workspace_id,
    )

    task = task_repository.get_task_by_id(
        session=session,
        task_id=task_id,
        workspace_id=workspace_id,
    )

    if task is None:
        raise ValueError("Task not found.")

    task_repository.delete_task_record(
        session=session,
        task=task,
    )

    return True