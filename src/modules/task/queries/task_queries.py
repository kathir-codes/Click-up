import strawberry
from uuid import UUID
from src.modules.user.services import get_profile
from src.core.database import SessionLocal
from src.core.dependencies import get_current_user_sub
from src.modules.task.types import (
    TaskType,
    TaskStatusType,
    TaskPriorityType,
)
from src.modules.task.services.task_service import (
    get_workspace_tasks,
    get_task_by_id,
    get_subtasks,
)
from src.modules.task.services.task_service import get_deleted_tasks
@strawberry.type
class TaskQuery:

    @strawberry.field
    def workspace_tasks(
        self,
        info: strawberry.Info,
        workspace_id: str,
    ) -> list[TaskType]:

        cognito_sub = get_current_user_sub(info)

        try:
            workspace_uuid = UUID(workspace_id)
        except ValueError:
            raise ValueError("Invalid workspace ID.")

        with SessionLocal() as session:

            profile = get_profile(
                session=session,
                cognito_sub=cognito_sub,
            )

            if profile is None:
                raise ValueError("User profile not found.")

            tasks = get_workspace_tasks(
                session=session,
                workspace_id=workspace_uuid,
                user_id=profile.user_id,
            )

            return [
                TaskType(
                    task_id=str(task.task_id),
                    workspace_id=str(task.workspace_id),
                    parent_task_id=(
                        str(task.parent_task_id)
                        if task.parent_task_id else None
                    ),
                    title=task.title,
                    description=task.description,
                    status=TaskStatusType(task.status.value),
                    priority=TaskPriorityType(task.priority.value),
                    assignee_id=(
                        str(task.assignee_id)
                        if task.assignee_id else None
                    ),
                    created_by=str(task.created_by),
                    due_date=task.due_date,
                    created_at=task.created_at,
                    updated_at=task.updated_at,
                )
                for task in tasks
            ]

    @strawberry.field
    def task_by_id(
        self,
        info: strawberry.Info,
        task_id: str,
        workspace_id: str,
    ) -> TaskType:

        cognito_sub = get_current_user_sub(info)

        try:
            task_uuid = UUID(task_id)
            workspace_uuid = UUID(workspace_id)
        except ValueError:
            raise ValueError("Invalid task ID or workspace ID.")

        with SessionLocal() as session:

            profile = get_profile(
                session=session,
                cognito_sub=cognito_sub,
            )

            if profile is None:
                raise ValueError("User profile not found.")

            task = get_task_by_id(
                session=session,
                task_id=task_uuid,
                workspace_id=workspace_uuid,
                user_id=profile.user_id,
            )

            return TaskType(
                task_id=str(task.task_id),
                workspace_id=str(task.workspace_id),
                parent_task_id=(
                    str(task.parent_task_id)
                    if task.parent_task_id else None
                ),
                title=task.title,
                description=task.description,
                status=TaskStatusType(task.status.value),
                priority=TaskPriorityType(task.priority.value),
                assignee_id=(
                    str(task.assignee_id)
                    if task.assignee_id else None
                ),
                created_by=str(task.created_by),
                due_date=task.due_date,
                created_at=task.created_at,
                updated_at=task.updated_at,
            )

    # -----------------------------
    # GET SUBTASKS
    # -----------------------------

    @strawberry.field
    def subtasks_by_parent(
        self,
        info: strawberry.Info,
        parent_task_id: str,
        workspace_id: str,
    ) -> list[TaskType]:

        cognito_sub = get_current_user_sub(info)

        try:
            parent_uuid = UUID(parent_task_id)
            workspace_uuid = UUID(workspace_id)

        except ValueError:
            raise ValueError(
                "Invalid parent task ID or workspace ID."
            )

        with SessionLocal() as session:

            profile = get_profile(
                session=session,
                cognito_sub=cognito_sub,
            )

            if profile is None:
                raise ValueError("User profile not found.")

            subtasks = get_subtasks(
                session=session,
                parent_task_id=parent_uuid,
                workspace_id=workspace_uuid,
                user_id=profile.user_id,
            )

            return [
                TaskType(
                    task_id=str(task.task_id),
                    workspace_id=str(task.workspace_id),
                    parent_task_id=str(task.parent_task_id),
                    title=task.title,
                    description=task.description,
                    status=TaskStatusType(task.status.value),
                    priority=TaskPriorityType(task.priority.value),
                    assignee_id=(
                        str(task.assignee_id)
                        if task.assignee_id else None
                    ),
                    created_by=str(task.created_by),
                    due_date=task.due_date,
                    created_at=task.created_at,
                    updated_at=task.updated_at,
                )
                for task in subtasks
            ]

    # -----------------------------
    # GET DELETED TASKS (TRASH)
    # -----------------------------

    @strawberry.field
    def deleted_tasks(
        self,
        info: strawberry.Info,
        workspace_id: str,
    ) -> list[TaskType]:

        cognito_sub = get_current_user_sub(info)

        try:
            workspace_uuid = UUID(workspace_id)
        except ValueError:
            raise ValueError("Invalid workspace ID.")

        with SessionLocal() as session:

            profile = get_profile(
                session=session,
                cognito_sub=cognito_sub,
            )

            if profile is None:
                raise ValueError("User profile not found.")

            tasks = get_deleted_tasks(
                session=session,
                workspace_id=workspace_uuid,
                user_id=profile.user_id,
            )

            return [
                TaskType(
                    task_id=str(task.task_id),
                    workspace_id=str(task.workspace_id),
                    parent_task_id=(
                        str(task.parent_task_id)
                        if task.parent_task_id else None
                    ),
                    title=task.title,
                    description=task.description,
                    status=TaskStatusType(task.status.value),
                    priority=TaskPriorityType(task.priority.value),
                    assignee_id=(
                        str(task.assignee_id)
                        if task.assignee_id else None
                    ),
                    created_by=str(task.created_by),
                    due_date=task.due_date,
                    created_at=task.created_at,
                    updated_at=task.updated_at,
                )
                for task in tasks
            ]