from uuid import UUID

import strawberry

from src.core.database import SessionLocal
from src.core.dependencies import get_current_user_sub
from src.modules.tag.services import (
    assign_tag_to_task,
    create_tag,
    remove_tag_from_task,
)
from src.modules.tag.types import TagType
from src.modules.user.services import get_profile


@strawberry.type
class TagMutation:

    # CREATE TAG

    @strawberry.mutation
    def create_tag(
        self,
        info: strawberry.Info,
        workspace_id: str,
        name: str,
    ) -> TagType:

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

            tag = create_tag(
                session=session,
                workspace_id=workspace_uuid,
                name=name,
                user_id=profile.user_id,
            )

            return TagType(
                tag_id=str(tag.tag_id),
                workspace_id=str(tag.workspace_id),
                name=tag.name,
                created_by=str(tag.created_by),
                created_at=tag.created_at,
            )

    # ASSIGN TAG TO TASK

    @strawberry.mutation
    def assign_tag_to_task(
        self,
        info: strawberry.Info,
        task_id: str,
        tag_id: str,
        workspace_id: str,
    ) -> TagType:

        cognito_sub = get_current_user_sub(info)

        try:
            task_uuid = UUID(task_id)
            tag_uuid = UUID(tag_id)
            workspace_uuid = UUID(workspace_id)

        except ValueError:
            raise ValueError("Invalid task, tag, or workspace ID.")

        with SessionLocal() as session:

            profile = get_profile(
                session=session,
                cognito_sub=cognito_sub,
            )

            if profile is None:
                raise ValueError("User profile not found.")

            tag = assign_tag_to_task(
                session=session,
                task_id=task_uuid,
                tag_id=tag_uuid,
                workspace_id=workspace_uuid,
                user_id=profile.user_id,
            )

            return TagType(
                tag_id=str(tag.tag_id),
                workspace_id=str(tag.workspace_id),
                name=tag.name,
                created_by=str(tag.created_by),
                created_at=tag.created_at,
            )

    # REMOVE TAG FROM TASK

    @strawberry.mutation
    def remove_tag_from_task(
        self,
        info: strawberry.Info,
        task_id: str,
        tag_id: str,
        workspace_id: str,
    ) -> bool:

        cognito_sub = get_current_user_sub(info)

        try:
            task_uuid = UUID(task_id)
            tag_uuid = UUID(tag_id)
            workspace_uuid = UUID(workspace_id)

        except ValueError:
            raise ValueError("Invalid task, tag, or workspace ID.")

        with SessionLocal() as session:

            profile = get_profile(
                session=session,
                cognito_sub=cognito_sub,
            )

            if profile is None:
                raise ValueError("User profile not found.")

            return remove_tag_from_task(
                session=session,
                task_id=task_uuid,
                tag_id=tag_uuid,
                workspace_id=workspace_uuid,
                user_id=profile.user_id,
            )
