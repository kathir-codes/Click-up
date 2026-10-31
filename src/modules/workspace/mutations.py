
import strawberry
from uuid import UUID

from src.core.database import SessionLocal
from src.core.jwt import validate_access_token
from src.modules.user.service import get_profile
from src.modules.authorization.service import check_workspace_permission
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

        authorization = info.context["request"].headers.get("Authorization")

        if not authorization or not authorization.startswith("Bearer "):
            raise ValueError("Bearer token required.")

        token = authorization.split(" ", 1)[1].strip()

        if not token:
            raise ValueError("Access token is missing.")

        try:
            claims = validate_access_token(token)
        except Exception as exc:
            raise ValueError("Invalid or expired access token.") from exc

        cognito_sub = claims["sub"]

        with SessionLocal() as session:
            profile = get_profile(
                session=session,
                cognito_sub=cognito_sub,
            )

            if profile is None:
                raise ValueError("User profile not found.")

            workspace = create_workspace(
                session=session,
                name=name,
                slug=slug,
                description=description,
                creator_user_id=profile.user_id,
            )

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

        authorization = info.context["request"].headers.get("Authorization")

        if not authorization or not authorization.startswith("Bearer "):
            raise ValueError("Bearer token required.")

        token = authorization.split(" ", 1)[1].strip()

        if not token:
            raise ValueError("Access token is missing.")

        try:
            claims = validate_access_token(token)
        except Exception as exc:
            raise ValueError("Invalid or expired access token.") from exc

        cognito_sub = claims["sub"]

        try:
            workspace_uuid = UUID(workspace_id)
        except ValueError as exc:
            raise ValueError("Invalid workspace ID.") from exc

        with SessionLocal() as session:
            profile = get_profile(
                session=session,
                cognito_sub=cognito_sub,
            )

            if profile is None:
                raise ValueError("User profile not found.")

            has_permission = check_workspace_permission(
                session=session,
                workspace_id=workspace_uuid,
                user_id=profile.user_id,
                permission_name="UPDATE_WORKSPACE",
            )

            if not has_permission:
                raise ValueError(
                    "You do not have permission to update this workspace."
                )

            workspace = update_workspace(
                session=session,
                workspace_id=workspace_uuid,
                name=name,
                slug=slug,
                description=description,
            )

            if workspace is None:
                raise ValueError("Workspace not found.")

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

        authorization = info.context["request"].headers.get("Authorization")

        if not authorization or not authorization.startswith("Bearer "):
            raise ValueError("Bearer token required.")

        token = authorization.split(" ", 1)[1].strip()

        if not token:
            raise ValueError("Access token is missing.")

        try:
            claims = validate_access_token(token)
        except Exception as exc:
            raise ValueError("Invalid or expired access token.") from exc

        cognito_sub = claims["sub"]

        try:
            workspace_uuid = UUID(workspace_id)
        except ValueError as exc:
            raise ValueError("Invalid workspace ID.") from exc

        with SessionLocal() as session:
            profile = get_profile(
                session=session,
                cognito_sub=cognito_sub,
            )

            if profile is None:
                raise ValueError("User profile not found.")

            has_permission = check_workspace_permission(
                session=session,
                workspace_id=workspace_uuid,
                user_id=profile.user_id,
                permission_name="DELETE_WORKSPACE",
            )

            if not has_permission:
                raise ValueError(
                    "You do not have permission to delete this workspace."
                )

            deleted = delete_workspace(
                session=session,
                workspace_id=workspace_uuid,
            )

            if not deleted:
                raise ValueError("Workspace not found.")

            return True
