import strawberry

from src.core.database import SessionLocal
from src.core.jwt import validate_access_token
from src.database.user_operations import get_user_profile
from src.modules.workspace.service import create_workspace
from src.modules.workspace.types import WorkspaceType


@strawberry.type
class WorkspaceMutation:

    @strawberry.mutation
    def create_workspace(
        self,
        info: strawberry.Info,
        name: str,
        slug: str,
        description: str | None = None,
    ) -> WorkspaceType:

        # 1. Read the Authorization header.
        authorization = info.context["request"].headers.get("Authorization")

        if not authorization or not authorization.startswith("Bearer "):
            raise ValueError("Bearer token required.")

        token = authorization.split(" ", 1)[1].strip()

        if not token:
            raise ValueError("Access token is missing.")

        # 2. Validate the Cognito access token.
        try:
            claims = validate_access_token(token)
        except Exception as exc:
            raise ValueError("Invalid or expired access token.") from exc

        cognito_sub = claims["sub"]

        # 3. Find the logged-in user's profile.
        with SessionLocal() as session:
            profile = get_user_profile(session, cognito_sub)

            if profile is None:
                raise ValueError("User profile not found.")

            # 4. Create the workspace.
            workspace = create_workspace(
                session=session,
                name=name,
                slug=slug,
                description=description,
                creator_user_id=profile.user_id,
            )

            # 5. Return the workspace details.
            return WorkspaceType(
                workspace_id=str(workspace.workspace_id),
                name=workspace.name,
                slug=workspace.slug,
                description=workspace.description,
            )