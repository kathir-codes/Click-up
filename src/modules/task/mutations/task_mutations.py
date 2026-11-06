
import strawberry

from uuid import UUID
from datetime import datetime

from src.core.database import SessionLocal
from src.core.dependencies import get_current_user_sub

from src.models.task import TaskStatus, TaskPriority
from src.modules.user.services import get_profile
from src.modules.task.services.task_service import create_subtask
from src.modules.task.types import (
    TaskType,
    TaskStatusType,
    TaskPriorityType,
)
from src.modules.task.services import (
    create_task_comment,
    update_task_comment,
    delete_task_comment,
)
from src.modules.task.types import TaskCommentType
from src.modules.task.services.task_service import (
    create_task,
    update_task,
    delete_task,
    assign_task,
)


@strawberry.type
class TaskMutation:

    # -----------------------------
    # CREATE TASK
    # -----------------------------

    @strawberry.mutation
    def create_task(
        self,
        info: strawberry.Info,
        workspace_id: str,
        title: str,
        description: str | None = None,
        status: TaskStatusType = TaskStatusType.TODO,
        priority: TaskPriorityType = TaskPriorityType.MEDIUM,
        assignee_id: str | None = None,
        due_date: datetime | None = None,
    ) -> TaskType:

        cognito_sub = get_current_user_sub(info)

        try:
            workspace_uuid = UUID(workspace_id)
            assignee_uuid = UUID(assignee_id) if assignee_id else None
        except ValueError:
            raise ValueError("Invalid workspace ID or assignee ID.")

        with SessionLocal() as session:

            profile = get_profile(
                session=session,
                cognito_sub=cognito_sub,
            )
      

            if profile is None:
                raise ValueError("User profile not found.")

            task = create_task(
                session=session,
                workspace_id=workspace_uuid,
                user_id=profile.user_id,
                title=title,
                description=description,
                status=TaskStatus(status.value),
                priority=TaskPriority(priority.value),
                assignee_id=assignee_uuid,
                due_date=due_date,
            )

            return TaskType(
                task_id=str(task.task_id),
                workspace_id=str(task.workspace_id),
                parent_task_id=str(task.parent_task_id) if task.parent_task_id else None,
                title=task.title,
                description=task.description,
                status=TaskStatusType(task.status.value),
                priority=TaskPriorityType(task.priority.value),
                assignee_id=str(task.assignee_id) if task.assignee_id else None,
                created_by=str(task.created_by),
                due_date=task.due_date,
                created_at=task.created_at,
                updated_at=task.updated_at,
            )


    # -----------------------------
    # UPDATE TASK
    # -----------------------------

    @strawberry.mutation
    def update_task(
        self,
        info: strawberry.Info,
        task_id: str,
        workspace_id: str,
        title: str | None = None,
        description: str | None = None,
        due_date: datetime | None = None,
        status: TaskStatusType | None = None,
        priority: TaskPriorityType | None = None,
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

            task = update_task(
                session=session,
                task_id=task_uuid,
                workspace_id=workspace_uuid,
                user_id=profile.user_id,
                title=title,
                description=description,
                due_date=due_date,
                status=TaskStatus(status.value) if status is not None else None,
                priority=TaskPriority(priority.value) if priority is not None else None,
            )

            return TaskType(
                task_id=str(task.task_id),
                workspace_id=str(task.workspace_id),
                parent_task_id=str(task.parent_task_id) if task.parent_task_id else None,
                title=task.title,
                description=task.description,
                status=TaskStatusType(task.status.value),
                priority=TaskPriorityType(task.priority.value),
                assignee_id=str(task.assignee_id) if task.assignee_id else None,
                created_by=str(task.created_by),
                due_date=task.due_date,
                created_at=task.created_at,
                updated_at=task.updated_at,
            )


    # -----------------------------
    # DELETE TASK
    # -----------------------------

    @strawberry.mutation
    def delete_task(
        self,
        info: strawberry.Info,
        task_id: str,
        workspace_id: str,
    ) -> bool:

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

            return delete_task(
                session=session,
                task_id=task_uuid,
                workspace_id=workspace_uuid,
                user_id=profile.user_id,
            )


    # -----------------------------
    # ASSIGN TASK
    # -----------------------------

    @strawberry.mutation
    def assign_task(
        self,
        info: strawberry.Info,
        task_id: str,
        workspace_id: str,
        assignee_id: str | None = None,
    ) -> TaskType:

        cognito_sub = get_current_user_sub(info)

        try:
            task_uuid = UUID(task_id)
            workspace_uuid = UUID(workspace_id)
            assignee_uuid = UUID(assignee_id) if assignee_id else None
        except ValueError:
            raise ValueError("Invalid task, workspace, or assignee ID.")

        with SessionLocal() as session:

            profile = get_profile(
                session=session,
                cognito_sub=cognito_sub,
            )

            if profile is None:
                raise ValueError("User profile not found.")

            task = assign_task(
                session=session,
                task_id=task_uuid,
                workspace_id=workspace_uuid,
                user_id=profile.user_id,
                assignee_id=assignee_uuid,
            )

            return TaskType(
                task_id=str(task.task_id),
                workspace_id=str(task.workspace_id),
                parent_task_id=str(task.parent_task_id) if task.parent_task_id else None,
                title=task.title,
                description=task.description,
                status=TaskStatusType(task.status.value),
                priority=TaskPriorityType(task.priority.value),
                assignee_id=str(task.assignee_id) if task.assignee_id else None,
                created_by=str(task.created_by),
                due_date=task.due_date,
                created_at=task.created_at,
                updated_at=task.updated_at,
            )



    # -----------------------------
    # CREATE SUBTASK
    # -----------------------------

    @strawberry.mutation
    def create_subtask(
        self,
        info: strawberry.Info,
        parent_task_id: str,
        workspace_id: str,
        title: str,
        description: str | None = None,
        status: TaskStatusType = TaskStatusType.TODO,
        priority: TaskPriorityType = TaskPriorityType.MEDIUM,
        assignee_id: str | None = None,
        due_date: datetime | None = None,
    ) -> TaskType:

        cognito_sub = get_current_user_sub(info)

        try:
            parent_uuid = UUID(parent_task_id)
            workspace_uuid = UUID(workspace_id)
            assignee_uuid = UUID(assignee_id) if assignee_id else None

        except ValueError:
            raise ValueError(
                "Invalid parent task ID, workspace ID, or assignee ID."
            )

        with SessionLocal() as session:

            profile = get_profile(
                session=session,
                cognito_sub=cognito_sub,
            )

            if profile is None:
                raise ValueError("User profile not found.")

            subtask = create_subtask(
                session=session,
                parent_task_id=parent_uuid,
                workspace_id=workspace_uuid,
                user_id=profile.user_id,
                title=title,
                description=description,
                status=TaskStatus(status.value),
                priority=TaskPriority(priority.value),
                assignee_id=assignee_uuid,
                due_date=due_date,
            )

            return TaskType(
                task_id=str(subtask.task_id),
                workspace_id=str(subtask.workspace_id),
                parent_task_id=str(subtask.parent_task_id),
                title=subtask.title,
                description=subtask.description,
                status=TaskStatusType(subtask.status.value),
                priority=TaskPriorityType(subtask.priority.value),
                assignee_id=(
                    str(subtask.assignee_id)
                    if subtask.assignee_id else None
                ),
                created_by=str(subtask.created_by),
                due_date=subtask.due_date,
                created_at=subtask.created_at,
                updated_at=subtask.updated_at,
            )
