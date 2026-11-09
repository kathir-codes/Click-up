from uuid import UUID

import strawberry

from src.core.database import SessionLocal
from src.core.dependencies import get_current_user_sub
from src.modules.tag.services import get_workspace_tags
from src.modules.tag.types import TagType
from src.modules.user.services import get_profile


@strawberry.type
class TagQuery:

    @strawberry.field
    def workspace_tags(
        self,
        info: strawberry.Info,
        workspace_id: str,
    ) -> list[TagType]:

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

            tags = get_workspace_tags(
                session=session,
                workspace_id=workspace_uuid,
                user_id=profile.user_id,
            )

            return [
                TagType(
                    tag_id=str(tag.tag_id),
                    workspace_id=str(tag.workspace_id),
                    name=tag.name,
                    created_by=str(tag.created_by),
                    created_at=tag.created_at,
                )
                for tag in tags
            ]
