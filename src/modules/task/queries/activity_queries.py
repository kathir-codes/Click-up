from uuid import UUID

import strawberry

from src.core.database import SessionLocal
from src.core.dependencies import get_current_user_sub
from src.modules.task.services.activity_service import get_task_activities
from src.modules.task.types import TaskActivityType
from src.modules.user.services import get_profile


@strawberry.type
class TaskActivityQuery:

    @strawberry.field
    def task_activity_history(
        self,
        info: strawberry.Info,
        task_id: str,
        workspace_id: str,
    ) -> list[TaskActivityType]:

        cognito_sub = get_current_user_sub(info)

        try:
            task_uuid = UUID(task_id)
            workspace_uuid = UUID(workspace_id)

        except ValueError:
            raise ValueError("Invalid task or workspace ID.")

        with SessionLocal() as session:

            profile = get_profile(
                session=session,
                cognito_sub=cognito_sub,
            )

            if profile is None:
                raise ValueError("User profile not found.")

            activities = get_task_activities(
                session=session,
                task_id=task_uuid,
                workspace_id=workspace_uuid,
                user_id=profile.user_id,
            )

            return [
                TaskActivityType(
                    activity_id=str(activity.activity_id),
                    task_id=str(activity.task_id),
                    user_id=(str(activity.user_id) if activity.user_id else None),
                    field=activity.field.value,
                    old_value=activity.old_value,
                    new_value=activity.new_value,
                    created_at=activity.created_at,
                )
                for activity in activities
            ]
