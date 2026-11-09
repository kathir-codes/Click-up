from uuid import UUID
from datetime import datetime

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
from src.modules.workspace.services.workspace_service import (
    check_workspace_is_active,
)

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