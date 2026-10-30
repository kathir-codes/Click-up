import strawberry
from uuid import UUID

from src.core.database import SessionLocal
from src.core.jwt import validate_access_token
from src.database.user_operations import get_user_profile
from src.database.role_permission_operations import (
    user_has_workspace_permission,
)
from src.modules.workspace.service import (
    create_workspace,
    update_workspace,
    delete_workspace,
)
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

    @strawberry.mutation
    def update_workspace(
        self,
        info: strawberry.Info,  
        workspace_id: str,
        name: str | None = None,
        slug: str | None = None,
        description: str | None = None,
    ) -> WorkspaceType:

        # 1. Get the Authorization header.
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
            raise ValueError(
                "Invalid or expired access token."
            ) from exc

        cognito_sub = claims["sub"]

        # 3. Validate the workspace ID.
        try:
            workspace_uuid = UUID(workspace_id)
        except ValueError as exc:
            raise ValueError("Invalid workspace ID.") from exc

        # 4. Get the logged-in user's profile.
        with SessionLocal() as session:
            profile = get_user_profile(session, cognito_sub)

            if profile is None:
                raise ValueError("User profile not found.")

            # 5. Check the user's workspace permission.
            has_permission = user_has_workspace_permission(
                session=session,
                workspace_id=workspace_uuid,
                user_id=profile.user_id,
                permission_name="UPDATE_WORKSPACE",
            )

            if not has_permission:
                raise ValueError(
                    "You do not have permission to update this workspace."
                )

            # 6. Update the workspace.
            workspace = update_workspace(
                session=session,
                workspace_id=workspace_uuid,
                name=name,
                slug=slug,
                description=description,
            )

            if workspace is None:
                raise ValueError("Workspace not found.")

            # 7. Return the updated workspace.
            return WorkspaceType(
                workspace_id=str(workspace.workspace_id),
                name=workspace.name,
                slug=workspace.slug,
                description=workspace.description,
            )

    @strawberry.mutation
    def delete_workspace(
        self,
        info: strawberry.Info,
        workspace_id: str,
    ) -> bool:

        # 1. Get the Authorization header.
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
            raise ValueError(
                "Invalid or expired access token."
            ) from exc

        cognito_sub = claims["sub"]

        # 3. Validate the workspace ID.
        try:
            workspace_uuid = UUID(workspace_id)
        except ValueError as exc:
            raise ValueError("Invalid workspace ID.") from exc

        # 4. Find the logged-in user's profile.
        with SessionLocal() as session:
            profile = get_user_profile(session, cognito_sub)

            if profile is None:
                raise ValueError("User profile not found.")

            # 5. Check DELETE_WORKSPACE permission.
            has_permission = user_has_workspace_permission(
                session=session,
                workspace_id=workspace_uuid,
                user_id=profile.user_id,
                permission_name="DELETE_WORKSPACE",
            )

            if not has_permission:
                raise ValueError(
                    "You do not have permission to delete this workspace."
                )

            # 6. Delete the workspace.
            deleted = delete_workspace(
                session=session,
                workspace_id=workspace_uuid,
            )

            if not deleted:
                raise ValueError("Workspace not found.")

            return True