
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
# CREATE SUBTASK
# -----------------------------

@require_workspace_permission(Permission.CREATE_TASK)
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
        # Check whether workspace is active
        check_workspace_is_active(
            session=session,
            workspace_id=workspace_id,
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
            raise ValueError("A subtask cannot have another subtask.")

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

@require_workspace_permission(Permission.VIEW_TASK)
def get_subtasks(
    session: Session,
    parent_task_id: UUID,
    workspace_id: UUID,
    user_id: UUID,
) -> list[Task]:

    # Check whether workspace is active
    check_workspace_is_active(
        session=session,
        workspace_id=workspace_id,
    )

    # Check parent task exists
    parent_task = task_repository.get_task_by_id(
        session=session,
        task_id=parent_task_id,
        workspace_id=workspace_id,
    )

    if parent_task is None:
        raise ValueError("Parent task not found.")

    if parent_task.deleted_at is not None:
        raise ValueError("Cannot access a deleted task.")

    if parent_task.parent_task_id is not None:
        raise ValueError("Subtasks cannot have their own subtasks.")

    return task_repository.get_subtasks_by_parent(
        session=session,
        parent_task_id=parent_task_id,
        workspace_id=workspace_id,
    )