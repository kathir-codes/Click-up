
from uuid import UUID

from sqlalchemy.orm import Session

from src.common.permissions import Permission
from src.models.task import (
    Task,
    TaskStatus,
    TaskPriority,
    TaskActivityField,
)
from src.modules.task.repositories import task_repository
from src.modules.task.services.activity_service import create_task_activity
from src.modules.authorization.service import check_workspace_permission
from datetime import datetime, timezone

# -----------------------------
# CREATE TASK
# -----------------------------

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
        has_permission = check_workspace_permission(
            session=session,
            workspace_id=workspace_id,
            user_id=user_id,
            permission_name=Permission.CREATE_TASK,
        )

        if not has_permission:
            raise ValueError("You do not have permission to create tasks.")
        
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
                raise ValueError(
                    "Assignee is not a member of this workspace."
                )

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

def get_workspace_tasks(
    session: Session,
    workspace_id: UUID,
    user_id: UUID,
) -> list[Task]:

    has_permission = check_workspace_permission(
        session=session,
        workspace_id=workspace_id,
        user_id=user_id,
        permission_name=Permission.VIEW_TASK,
    )

    if not has_permission:
        raise ValueError(
            "You do not have permission to view workspace tasks."
        )

    return task_repository.get_tasks_by_workspace(
        session=session,
        workspace_id=workspace_id,
    )


# -----------------------------
# GET TASK BY ID
# -----------------------------

def get_task_by_id(
    session: Session,
    task_id: UUID,
    workspace_id: UUID,
    user_id: UUID,
) -> Task:

    has_permission = check_workspace_permission(
        session=session,
        workspace_id=workspace_id,
        user_id=user_id,
        permission_name=Permission.VIEW_TASK,
    )

    if not has_permission:
        raise ValueError(
            "You do not have permission to view this task."
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
        has_permission = check_workspace_permission(
            session=session,
            workspace_id=workspace_id,
            user_id=user_id,
            permission_name=Permission.UPDATE_TASK,
        )

        if not has_permission:
            raise ValueError(
                "You do not have permission to update tasks."
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

def delete_task(
    session: Session,
    task_id: UUID,
    workspace_id: UUID,
    user_id: UUID,
) -> bool:

    try:
        has_permission = check_workspace_permission(
            session=session,
            workspace_id=workspace_id,
            user_id=user_id,
            permission_name=Permission.DELETE_TASK,
        )

        if not has_permission:
            raise ValueError(
                "You do not have permission to delete tasks."
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


# -----------------------------
# ASSIGN TASK
# -----------------------------

def assign_task(
    session: Session,
    task_id: UUID,
    workspace_id: UUID,
    user_id: UUID,
    assignee_id: UUID | None,
) -> Task:

    try:
        has_permission = check_workspace_permission(
            session=session,
            workspace_id=workspace_id,
            user_id=user_id,
            permission_name=Permission.ASSIGN_TASK,
        )

        if not has_permission:
            raise ValueError(
                "You do not have permission to assign tasks."
            )

        task = task_repository.get_task_by_id(
            session=session,
            task_id=task_id,
            workspace_id=workspace_id,
        )

        if task is None:
            raise ValueError("Task not found.")

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
                raise ValueError(
                    "Assignee is not a member of this workspace."
                )

        old_assignee_id = task.assignee_id

        task = task_repository.assign_task_record(
            session=session,
            task=task,
            assignee_id=assignee_id,
        )

        # Record assignee change
        if old_assignee_id != task.assignee_id:
            create_task_activity(
                session=session,
                task_id=task.task_id,
                user_id=user_id,
                field=TaskActivityField.ASSIGNEE,
                old_value=(
                    str(old_assignee_id)
                    if old_assignee_id else None
                ),
                new_value=(
                    str(task.assignee_id)
                    if task.assignee_id else None
                ),
            )

        session.commit()
        session.refresh(task)

        return task

    except Exception:
        session.rollback()
        raise


# -----------------------------
# CREATE SUBTASK
# -----------------------------

def create_subtask(
    session: Session,
    parent_task_id: UUID,
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
        # Check permission
        has_permission = check_workspace_permission(
            session=session,
            workspace_id=workspace_id,
            user_id=user_id,
            permission_name=Permission.CREATE_TASK,
        )

        if not has_permission:
            raise ValueError(
                "You do not have permission to create subtasks."
            )

        # Find parent task
        parent_task = task_repository.get_task_by_id(
            session=session,
            task_id=parent_task_id,
            workspace_id=workspace_id,
        )

        if parent_task is None:
            raise ValueError("Parent task not found.")

        if parent_task.deleted_at is not None:
            raise ValueError("Cannot create a subtask under a deleted task.")

        # Prevent nested subtasks
        if parent_task.parent_task_id is not None:
            raise ValueError(
                "A subtask cannot have another subtask."
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
                raise ValueError(
                    "Assignee is not a member of this workspace."
                )

        # Create subtask
        subtask = task_repository.create_subtask_record(
            session=session,
            parent_task=parent_task,
            title=title,
            description=description,
            created_by=user_id,
            status=status,
            priority=priority,
            assignee_id=assignee_id,
            due_date=due_date,
        )

        # Record activity
        create_task_activity(
            session=session,
            task_id=subtask.task_id,
            user_id=user_id,
            field=TaskActivityField.TASK_CREATED,
            old_value=None,
            new_value=subtask.title,
        )

        session.commit()
        session.refresh(subtask)

        return subtask

    except Exception:
        session.rollback()
        raise


# -----------------------------
# GET SUBTASKS
# -----------------------------

def get_subtasks(
    session: Session,
    parent_task_id: UUID,
    workspace_id: UUID,
    user_id: UUID,
) -> list[Task]:

    has_permission = check_workspace_permission(
        session=session,
        workspace_id=workspace_id,
        user_id=user_id,
        permission_name=Permission.VIEW_TASK,
    )

    if not has_permission:
        raise ValueError(
            "You do not have permission to view subtasks."
        )

    # Check parent task exists
    parent_task = task_repository.get_task_by_id(
        session=session,
        task_id=parent_task_id,
        workspace_id=workspace_id,
    )

    if parent_task is None:
        raise ValueError("Parent task not found.")

    if parent_task.parent_task_id is not None:
        raise ValueError(
            "Subtasks cannot have their own subtasks."
        )

    return task_repository.get_subtasks_by_parent(
        session=session,
        parent_task_id=parent_task_id,
        workspace_id=workspace_id,
    )