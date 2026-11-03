import strawberry

from uuid import UUID

from src.core.database import SessionLocal
from src.core.dependencies import get_current_user_sub

from src.modules.user.service import get_profile
from src.modules.workspace.service import (
    get_user_workspaces,
    get_user_workspace,
)

from src.modules.workspace.types import WorkspaceType


@strawberry.type
class WorkspaceQuery:

    # -----------------------------
    # GET MY WORKSPACES
    # -----------------------------

    @strawberry.field
    def my_workspaces(
        self,
        info: strawberry.Info,
    ) -> list[WorkspaceType]:

        cognito_sub = get_current_user_sub(info)

        with SessionLocal() as session:

            profile = get_profile(
                session=session,
                cognito_sub=cognito_sub,
            )

            if profile is None:
                raise ValueError("User profile not found.")

            workspaces = get_user_workspaces(
                session=session,
                user_id=profile.user_id,
            )

            return [
                WorkspaceType(
                    workspace_id=str(workspace.workspace_id),
                    name=workspace.name,
                    slug=workspace.slug,
                    description=workspace.description,
                )
                for workspace in workspaces
            ]

    # -----------------------------
    # GET SINGLE WORKSPACE
    # -----------------------------

    @strawberry.field
    def workspace(
        self,
        info: strawberry.Info,
        workspace_id: str,
    ) -> WorkspaceType | None:

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

            workspace = get_user_workspace(
                session=session,
                workspace_id=workspace_uuid,
                user_id=profile.user_id,
            )

            if workspace is None:
                return None

            return WorkspaceType(
                workspace_id=str(workspace.workspace_id),
                name=workspace.name,
                slug=workspace.slug,
                description=workspace.description,
            )