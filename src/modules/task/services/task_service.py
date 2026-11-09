
from datetime import datetime
from uuid import UUID

from sqlalchemy.orm import Session

from src.common.permissions import Permission
from src.models.task import Task, TaskActivityField, TaskPriority, TaskStatus
from src.modules.authorization.decorators import require_workspace_permission
from src.modules.task.repositories import task_repository
from src.modules.task.services.activity_service import create_task_activity
from src.modules.workspace.services.workspace_service import check_workspace_is_active


# -----------------------------
# CREATE TASK
# -----------------------------

@require_workspace_permission(Permission.CREATE_TASK)
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

    try:
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

        create_task_activity(
            session=session,
            task_id=task.task_id,
            user_id=user_id,
            field=TaskActivityField.TASK_CREATED,
            old_value=None,
            new_value=task.title,
        )

        session.commit()
        session.refresh(task)

        return task

    except Exception:
        session.rollback()
        raise


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

    try:
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

        old_title = task.title
        old_description = task.description
        old_status = task.status
        old_priority = task.priority

        task = task_repository.update_task_record(
            session=session,
            task=task,
            title=title,
            description=description,
            due_date=due_date,
            status=status,
            priority=priority,
        )

        # Record title change
        if title is not None and old_title != task.title:
            create_task_activity(
                session=session,
                task_id=task.task_id,
                user_id=user_id,
                field=TaskActivityField.TITLE,
                old_value=old_title,
                new_value=task.title,
            )

        # Record description change
        if description is not None and old_description != task.description:
            create_task_activity(
                session=session,
                task_id=task.task_id,
                user_id=user_id,
                field=TaskActivityField.DESCRIPTION,
                old_value=old_description,
                new_value=task.description,
            )

        # Record status change
        if status is not None and old_status != task.status:
            create_task_activity(
                session=session,
                task_id=task.task_id,
                user_id=user_id,
                field=TaskActivityField.STATUS,
                old_value=old_status.value,
                new_value=task.status.value,
            )

        # Record priority change
        if priority is not None and old_priority != task.priority:
            create_task_activity(
                session=session,
                task_id=task.task_id,
                user_id=user_id,
                field=TaskActivityField.PRIORITY,
                old_value=old_priority.value,
                new_value=task.priority.value,
            )

        session.commit()
        session.refresh(task)

        return task

    except Exception:
        session.rollback()
        raise


# -----------------------------
# DELETE TASK
# -----------------------------

@require_workspace_permission(Permission.DELETE_TASK)
def delete_task(
    session: Session,
    task_id: UUID,
    workspace_id: UUID,
    user_id: UUID,
) -> bool:

    try:
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

        session.commit()
        return True

    except Exception:
        session.rollback()
        raise
