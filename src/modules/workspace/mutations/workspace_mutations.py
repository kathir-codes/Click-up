
import strawberry

from src.core.database import SessionLocal
from src.core.dependencies import get_current_user_sub
from src.modules.user.services import get_profile
from src.modules.workspace.services import (
    create_workspace,
    delete_workspace,
    remove_workspace_member,
    restore_workspace as restore_workspace_service,
    update_workspace,
)
from src.modules.workspace.types import WorkspaceType
from src.modules.workspace.validations import (
    CreateWorkspacePayload,
    RemoveWorkspaceMemberPayload,
    UpdateWorkspacePayload,
    WorkspaceIDPayload,
)

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

        validated_data = CreateWorkspacePayload(
            name=name,
            slug=slug,
            description=description,
        )

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
                name=validated_data.name,
                slug=validated_data.slug,
                description=validated_data.description,
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

        validated_data = UpdateWorkspacePayload(
            name=name,
            slug=slug,
            description=description,
        )

        workspace_id_data = WorkspaceIDPayload(
            workspace_id=workspace_id,
        )

        cognito_sub = get_current_user_sub(info)

        with SessionLocal() as session:
            profile = get_profile(
                session=session,
                cognito_sub=cognito_sub,
            )

            if profile is None:
                raise ValueError("User profile not found.")

            workspace = update_workspace(
                session=session,
                workspace_id=workspace_id_data.workspace_id,
                user_id=profile.user_id,
                name=validated_data.name,
                slug=validated_data.slug,
                description=validated_data.description,
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

        workspace_id_data = WorkspaceIDPayload(
            workspace_id=workspace_id,
        )

        cognito_sub = get_current_user_sub(info)

        with SessionLocal() as session:
            profile = get_profile(
                session=session,
                cognito_sub=cognito_sub,
            )

            if profile is None:
                raise ValueError("User profile not found.")

            deleted = delete_workspace(
                session=session,
                workspace_id=workspace_id_data.workspace_id,
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

        validated_data = RemoveWorkspaceMemberPayload(
            workspace_id=workspace_id,
            target_user_id=target_user_id,
        )

        cognito_sub = get_current_user_sub(info)

        with SessionLocal() as session:
            profile = get_profile(
                session=session,
                cognito_sub=cognito_sub,
            )

            if profile is None:
                raise ValueError("User profile not found.")

            removed = remove_workspace_member(
                session=session,
                workspace_id=validated_data.workspace_id,
                user_id=profile.user_id,
                target_user_id=validated_data.target_user_id,
            )

            return removed

    # -----------------------------
    # RESTORE WORKSPACE
    # -----------------------------

    @strawberry.mutation
    def restore_workspace(
        self,
        info: strawberry.Info,
        workspace_id: str,
    ) -> bool:

        workspace_id_data = WorkspaceIDPayload(
            workspace_id=workspace_id,
        )

        cognito_sub = get_current_user_sub(info)

        with SessionLocal() as session:
            profile = get_profile(
                session=session,
                cognito_sub=cognito_sub,
            )

            if profile is None:
                raise ValueError("User profile not found.")

            restored = restore_workspace_service(
                session=session,
                workspace_id=workspace_id_data.workspace_id,
                user_id=profile.user_id,
            )

            if not restored:
                raise ValueError("Deleted workspace not found.")

            return True
