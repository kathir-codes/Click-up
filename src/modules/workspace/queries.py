import strawberry
from sqlalchemy import select

from src.core.database import SessionLocal
from src.core.jwt import validate_access_token
from src.database.user_operations import get_user_profile
from src.models.workspace import Workspace, WorkspaceMember
from src.modules.workspace.types import WorkspaceType


@strawberry.type
class WorkspaceQuery:

    @strawberry.field
    def my_workspaces(self, info: strawberry.Info) -> list[WorkspaceType]:
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
            profile = get_user_profile(session, cognito_sub)

            if profile is None:
                raise ValueError("User profile not found.")

            # 4. Find workspaces where this user is a member
            statement = (
                select(Workspace)
                .join(
                    WorkspaceMember,
                    Workspace.workspace_id == WorkspaceMember.workspace_id,
                )
                .where(WorkspaceMember.user_id == profile.user_id)
                .order_by(Workspace.created_at.desc())
            )

            workspaces = session.scalars(statement).all()

            # 5. Return the workspace data
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

        # 3. Find the user's profile
        with SessionLocal() as session:
            profile = get_user_profile(session, cognito_sub)

            if profile is None:
                raise ValueError("User profile not found.")

            # 4. Find the requested workspace only if the user is a member
            statement = (
                select(Workspace)
                .join(
                    WorkspaceMember,
                    Workspace.workspace_id == WorkspaceMember.workspace_id,
                )
                .where(
                    Workspace.workspace_id == workspace_id,
                    WorkspaceMember.user_id == profile.user_id,
                )
            )

            workspace = session.scalar(statement)

            if workspace is None:
                return None

            # 5. Return workspace details
            return WorkspaceType(
                workspace_id=str(workspace.workspace_id),
                name=workspace.name,
                slug=workspace.slug,
                description=workspace.description,
            )