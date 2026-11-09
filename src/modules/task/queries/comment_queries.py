from uuid import UUID

import strawberry

from src.core.database import SessionLocal
from src.core.dependencies import get_current_user_sub
from src.modules.task.services import get_task_comments
from src.modules.task.types import TaskCommentType
from src.modules.user.services import get_profile


@strawberry.type
class TaskCommentQuery:

    @strawberry.field
    def task_comments(
        self,
        info: strawberry.Info,
        task_id: str,
        workspace_id: str,
    ) -> list[TaskCommentType]:
        session = SessionLocal()

        try:
            cognito_sub = get_current_user_sub(info)

            user = get_profile(
                session=session,
                cognito_sub=cognito_sub,
            )

            if user is None:
                raise ValueError("User profile not found.")

            comments = get_task_comments(
                session=session,
                task_id=UUID(task_id),
                workspace_id=UUID(workspace_id),
                user_id=user.user_id,
            )

            return [
                TaskCommentType(
                    comment_id=str(comment.comment_id),
                    task_id=str(comment.task_id),
                    user_id=str(comment.user_id),
                    content=comment.content,
                    created_at=comment.created_at,
                    updated_at=comment.updated_at,
                )
                for comment in comments
            ]

        finally:
            session.close()
