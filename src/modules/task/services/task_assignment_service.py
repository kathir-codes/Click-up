
from uuid import UUID

from sqlalchemy.orm import Session

from src.common.permissions import Permission
from src.models.task import Task, TaskActivityField
from src.modules.authorization.decorators import require_workspace_permission
from src.modules.task.repositories import task_repository
from src.modules.task.services.activity_service import create_task_activity
from src.modules.workspace.services.workspace_service import check_workspace_is_active


# -----------------------------
# ASSIGN TASK
# -----------------------------

@require_workspace_permission(Permission.ASSIGN_TASK)
def assign_task(
    session: Session,
    task_id: UUID,
    workspace_id: UUID,
    user_id: UUID,
    assignee_id: UUID | None,
) -> Task:

    try:
        # Check whether workspace is active
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
                old_value=(str(old_assignee_id) if old_assignee_id else None),
                new_value=(str(task.assignee_id) if task.assignee_id else None),
            )

        session.commit()
        session.refresh(task)

        return task

    except Exception:
        session.rollback()
        raise
