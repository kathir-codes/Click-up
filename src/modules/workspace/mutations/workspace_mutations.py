import strawberry
import logging

from uuid import UUID

from src.core.database import SessionLocal
from src.core.dependencies import get_current_user_sub
from src.modules.user.services import get_profile
from src.modules.workspace.services import (
    create_workspace,
    update_workspace,
    delete_workspace,
    remove_workspace_member,
)

from src.modules.workspace.types import WorkspaceType


@strawberry.type
class WorkspaceMutation:

    # -----------------------------
    # CREATE WORKSPACE
    # -----------------------------

    @strawberry.mutation
    def create_workspace(
        self,
        info: strawberry.Info,
        name: str,
        slug: str,
        description: str | None = None,
    ) -> WorkspaceType:
        cognito_sub = get_current_user_sub(info)

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

    # -----------------------------
    # UPDATE WORKSPACE
    # -----------------------------

    @strawberry.mutation
    def update_workspace(
        self,
        info: strawberry.Info,
        workspace_id: str,
        name: str | None = None,
        slug: str | None = None,
        description: str | None = None,
    ) -> WorkspaceType:

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

            workspace = update_workspace(
                session=session,
                workspace_id=workspace_uuid,
                user_id=profile.user_id,
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

    # -----------------------------
    # DELETE WORKSPACE
    # -----------------------------

    @strawberry.mutation
    def delete_workspace(
        self,
        info: strawberry.Info,
        workspace_id: str,
    ) -> bool:

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

            deleted = delete_workspace(
                session=session,
                workspace_id=workspace_uuid,
                user_id=profile.user_id,
            )

            if not deleted:
                raise ValueError("Workspace not found.")

            return True


    # -----------------------------
    # REMOVE WORKSPACE MEMBER
    # -----------------------------

    @strawberry.mutation
    def remove_workspace_member(
        self,
        info: strawberry.Info,
        workspace_id: str,
        target_user_id: str,
    ) -> bool:

        cognito_sub = get_current_user_sub(info)

        try:
            workspace_uuid = UUID(workspace_id)
            target_user_uuid = UUID(target_user_id)
        except ValueError:
            raise ValueError("Invalid workspace ID or target user ID.")

        with SessionLocal() as session:

            profile = get_profile(
                session=session,
                cognito_sub=cognito_sub,
            )

            if profile is None:
                raise ValueError("User profile not found.")

            removed = remove_workspace_member(
                session=session,
                workspace_id=workspace_uuid,
                requester_user_id=profile.user_id,
                target_user_id=target_user_uuid,
            )

            return removed
