from uuid import UUID

import strawberry

from src.core.database import SessionLocal
from src.core.dependencies import get_current_user_sub
from src.modules.task.services import (
    create_task_comment,
    delete_task_comment,
    update_task_comment,
)
from src.modules.task.types import TaskCommentType
from src.modules.user.services import get_profile


@strawberry.type
class TaskCommentMutation:

    # -----------------------------
    # CREATE TASK COMMENT
    # -----------------------------

    @strawberry.mutation
    def create_task_comment(
        self,
        info: strawberry.Info,
        task_id: str,
        workspace_id: str,
        content: str,
    ) -> TaskCommentType:

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

            comment = create_task_comment(
                session=session,
                task_id=task_uuid,
                workspace_id=workspace_uuid,
                user_id=profile.user_id,
                content=content,
            )

            return TaskCommentType(
                comment_id=str(comment.comment_id),
                task_id=str(comment.task_id),
                user_id=str(comment.user_id),
                content=comment.content,
                created_at=comment.created_at,
                updated_at=comment.updated_at,
            )

    # -----------------------------
    # UPDATE TASK COMMENT
    # -----------------------------

    @strawberry.mutation
    def update_task_comment(
        self,
        info: strawberry.Info,
        comment_id: str,
        task_id: str,
        workspace_id: str,
        content: str,
    ) -> TaskCommentType:

        cognito_sub = get_current_user_sub(info)

        try:
            comment_uuid = UUID(comment_id)
            task_uuid = UUID(task_id)
            workspace_uuid = UUID(workspace_id)
        except ValueError:
            raise ValueError("Invalid comment, task, or workspace ID.")

        with SessionLocal() as session:

            profile = get_profile(
                session=session,
                cognito_sub=cognito_sub,
            )

            if profile is None:
                raise ValueError("User profile not found.")

            comment = update_task_comment(
                session=session,
                comment_id=comment_uuid,
                task_id=task_uuid,
                workspace_id=workspace_uuid,
                user_id=profile.user_id,
                content=content,
            )

            return TaskCommentType(
                comment_id=str(comment.comment_id),
                task_id=str(comment.task_id),
                user_id=str(comment.user_id),
                content=comment.content,
                created_at=comment.created_at,
                updated_at=comment.updated_at,
            )

    # -----------------------------
    # DELETE TASK COMMENT
    # -----------------------------

    @strawberry.mutation
    def delete_task_comment(
        self,
        info: strawberry.Info,
        comment_id: str,
        task_id: str,
        workspace_id: str,
    ) -> bool:

        cognito_sub = get_current_user_sub(info)

        try:
            comment_uuid = UUID(comment_id)
            task_uuid = UUID(task_id)
            workspace_uuid = UUID(workspace_id)
        except ValueError:
            raise ValueError("Invalid comment, task, or workspace ID.")

        with SessionLocal() as session:

            profile = get_profile(
                session=session,
                cognito_sub=cognito_sub,
            )

            if profile is None:
                raise ValueError("User profile not found.")

            return delete_task_comment(
                session=session,
                comment_id=comment_uuid,
                task_id=task_uuid,
                workspace_id=workspace_uuid,
                user_id=profile.user_id,
            )
