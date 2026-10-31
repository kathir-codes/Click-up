import strawberry

from uuid import UUID

from src.core.database import SessionLocal
from src.core.jwt import validate_access_token
from src.modules.user.service import get_profile
from src.modules.workspace.service import (
    get_user_workspaces,
    get_user_workspace,
)
from src.modules.workspace.types import WorkspaceType


@strawberry.type
class WorkspaceQuery:

    @strawberry.field
    def my_workspaces(
        self,
        info: strawberry.Info,
    ) -> list[WorkspaceType]:

        # 1. Get the Authorization header
        authorization = info.context["request"].headers.get("Authorization")

        if not authorization or not authorization.startswith("Bearer "):
            raise ValueError("Bearer token required.")

        token = authorization.split(" ", 1)[1].strip()

        if not token:
            raise ValueError("Access token is missing.")

        # 2. Validate the Cognito access token
        try:
            claims = validate_access_token(token)
        except Exception as exc:
            raise ValueError("Invalid or expired access token.") from exc

        cognito_sub = claims["sub"]

        # 3. Find the logged-in user's profile
        with SessionLocal() as session:
            profile = get_profile(
                session=session,
                cognito_sub=cognito_sub,
            )

            if profile is None:
                raise ValueError("User profile not found.")

            # 4. Fetch workspaces through the service layer
            workspaces = get_user_workspaces(
                session=session,
                user_id=profile.user_id,
            )

            # 5. Return workspace details
            return [
                WorkspaceType(
                    workspace_id=str(workspace.workspace_id),
                    name=workspace.name,
                    slug=workspace.slug,
                    description=workspace.description,
                )
                for workspace in workspaces
            ]

    @strawberry.field
    def workspace(
        self,
        info: strawberry.Info,
        workspace_id: str,
    ) -> WorkspaceType | None:

        # 1. Get the Authorization header
        authorization = info.context["request"].headers.get("Authorization")

        if not authorization or not authorization.startswith("Bearer "):
            raise ValueError("Bearer token required.")

        token = authorization.split(" ", 1)[1].strip()

        if not token:
            raise ValueError("Access token is missing.")

        # 2. Validate the Cognito access token
        try:
            claims = validate_access_token(token)
        except Exception as exc:
            raise ValueError("Invalid or expired access token.") from exc

        cognito_sub = claims["sub"]

        # 3. Validate the workspace ID
        try:
            workspace_uuid = UUID(workspace_id)
        except ValueError as exc:
            raise ValueError("Invalid workspace ID.") from exc

        # 4. Find the logged-in user's profile
        with SessionLocal() as session:
            profile = get_profile(
                session=session,
                cognito_sub=cognito_sub,
            )

            if profile is None:
                raise ValueError("User profile not found.")

            # 5. Fetch the workspace through the service layer
            workspace = get_user_workspace(
                session=session,
                workspace_id=workspace_uuid,
                user_id=profile.user_id,
            )

            # 6. Return None if the workspace doesn't exist
            # or the user isn't a member
            if workspace is None:
                return None

            # 7. Return workspace details
            return WorkspaceType(
                workspace_id=str(workspace.workspace_id),
                name=workspace.name,
                slug=workspace.slug,
                description=workspace.description,
            )
