
import strawberry

from uuid import UUID

from src.core.database import SessionLocal
from src.core.dependencies import get_current_user_sub
from src.modules.invitation.service import (
    create_workspace_invitation,
    accept_workspace_invitation as accept_invitation_service,
    decline_workspace_invitation as decline_invitation_service,
    resend_workspace_invitation,
    cancel_workspace_invitation,
)
from src.modules.user.service import get_profile
from src.modules.authorization.service import check_workspace_permission
from src.modules.invitation.service import create_workspace_invitation
from src.modules.invitation.types import InvitationType, InvitationStatusType
from src.models.invitation import Invitation

@strawberry.type
class InvitationMutation:

    # -----------------------------
    # CREATE WORKSPACE INVITATION
    # -----------------------------

    @strawberry.mutation
    def create_workspace_invitation(
        self,
        info: strawberry.Info,
        workspace_id: str,
        email: str,
        role_name: str,
    ) -> InvitationType:

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

            # Check INVITE_MEMBER permission
            has_permission = check_workspace_permission(
                session=session,
                workspace_id=workspace_uuid,
                user_id=profile.user_id,
                permission_name="INVITE_MEMBER",
            )

            if not has_permission:
                raise ValueError(
                    "You don't have permission to invite members."
                )

            invitation, token = create_workspace_invitation(
                session=session,
                workspace_id=workspace_uuid,
                invited_by=profile.user_id,
                email=email,
                role_name=role_name,
            )

            return InvitationType(
                invitation_id=str(invitation.invitation_id),
                workspace_id=str(invitation.workspace_id),
                invited_by=str(invitation.invited_by),
                email=invitation.email,
                role_id=str(invitation.role_id),
                status=InvitationStatusType(invitation.status),
                expires_at=invitation.expires_at,
                accepted_at=invitation.accepted_at,
                created_at=invitation.created_at,
                token=token,
            )

    # -----------------------------
    # ACCEPT WORKSPACE INVITATION
    # -----------------------------

    @strawberry.mutation
    def accept_workspace_invitation(
        self,
        info: strawberry.Info,
        token: str,
    ) -> InvitationType:

        cognito_sub = get_current_user_sub(info)

        with SessionLocal() as session:

            # 1. Get logged-in user's profile
            profile = get_profile(
                session=session,
                cognito_sub=cognito_sub,
            )

            if profile is None:
                raise ValueError("User profile not found.")

            # 2. Accept invitation
            invitation = accept_invitation_service(
                session=session,
                token=token,
                user_id=profile.user_id,
                email=profile.user.email,
            )

            # 3. Return invitation details
            return InvitationType(
                invitation_id=str(invitation.invitation_id),
                workspace_id=str(invitation.workspace_id),
                invited_by=str(invitation.invited_by),
                email=invitation.email,
                role_id=str(invitation.role_id),
                status=InvitationStatusType(invitation.status.value),
                expires_at=invitation.expires_at,
                accepted_at=invitation.accepted_at,
                created_at=invitation.created_at,
            )



    # -----------------------------
    # RESEND WORKSPACE INVITATION
    # -----------------------------

    @strawberry.mutation
    def resend_workspace_invitation(
        self,
        info: strawberry.Info,
        invitation_id: str,
    ) -> InvitationType:

        cognito_sub = get_current_user_sub(info)

        try:
            invitation_uuid = UUID(invitation_id)
        except ValueError:
            raise ValueError("Invalid invitation ID.")

        with SessionLocal() as session:

            # 1. Get logged-in user's profile
            profile = get_profile(
                session=session,
                cognito_sub=cognito_sub,
            )

            if profile is None:
                raise ValueError("User profile not found.")

            # 2. Find invitation
            invitation = session.get(
                Invitation,
                invitation_uuid,
            )

            if invitation is None:
                raise ValueError("Invitation not found.")

            # 3. Check RESEND_INVITATION permission
            has_permission = check_workspace_permission(
                session=session,
                workspace_id=invitation.workspace_id,
                user_id=profile.user_id,
                permission_name="RESEND_INVITATION",
            )

            if not has_permission:
                raise ValueError(
                    "You don't have permission to resend invitations."
                )

            # 4. Resend invitation
            invitation, token = resend_workspace_invitation(
                session=session,
                invitation_id=invitation_uuid,
            )

            # 5. Return invitation details
            return InvitationType(
                invitation_id=str(invitation.invitation_id),
                workspace_id=str(invitation.workspace_id),
                invited_by=str(invitation.invited_by),
                email=invitation.email,
                role_id=str(invitation.role_id),
                status=InvitationStatusType(invitation.status.value),
                expires_at=invitation.expires_at,
                accepted_at=invitation.accepted_at,
                created_at=invitation.created_at,
                token=token,
            )


    # -----------------------------
    # CANCEL WORKSPACE INVITATION
    # -----------------------------

    @strawberry.mutation
    def cancel_workspace_invitation(
        self,
        info: strawberry.Info,
        invitation_id: str,
    ) -> InvitationType:

        cognito_sub = get_current_user_sub(info)

        try:
            invitation_uuid = UUID(invitation_id)
        except ValueError:
            raise ValueError("Invalid invitation ID.")

        with SessionLocal() as session:

            # 1. Get logged-in user's profile
            profile = get_profile(
                session=session,
                cognito_sub=cognito_sub,
            )

            if profile is None:
                raise ValueError("User profile not found.")

            # 2. Find invitation
            invitation = session.get(
                Invitation,
                invitation_uuid,
            )

            if invitation is None:
                raise ValueError("Invitation not found.")

            # 3. Check CANCEL_INVITATION permission
            has_permission = check_workspace_permission(
                session=session,
                workspace_id=invitation.workspace_id,
                user_id=profile.user_id,
                permission_name="CANCEL_INVITATION",
            )

            if not has_permission:
                raise ValueError(
                    "You don't have permission to cancel invitations."
                )

            # 4. Cancel invitation
            invitation = cancel_workspace_invitation(
                session=session,
                invitation_id=invitation_uuid,
            )

            # 5. Return invitation details
            return InvitationType(
                invitation_id=str(invitation.invitation_id),
                workspace_id=str(invitation.workspace_id),
                invited_by=str(invitation.invited_by),
                email=invitation.email,
                role_id=str(invitation.role_id),
                status=InvitationStatusType(invitation.status.value),
                expires_at=invitation.expires_at,
                accepted_at=invitation.accepted_at,
                created_at=invitation.created_at,
            )


    # -----------------------------
    # DECLINE WORKSPACE INVITATION
    # -----------------------------

    @strawberry.mutation
    def decline_workspace_invitation(
        self,
        info: strawberry.Info,
        token: str,
    ) -> InvitationType:

        cognito_sub = get_current_user_sub(info)

        with SessionLocal() as session:

            # 1. Get logged-in user's profile
            profile = get_profile(
                session=session,
                cognito_sub=cognito_sub,
            )

            if profile is None:
                raise ValueError("User profile not found.")

            # 2. Decline invitation
            invitation = decline_invitation_service(
                session=session,
                token=token,
                user_id=profile.user_id,
                email=profile.user.email,
            )

            # 3. Return invitation details
            return InvitationType(
                invitation_id=str(invitation.invitation_id),
                workspace_id=str(invitation.workspace_id),
                invited_by=str(invitation.invited_by),
                email=invitation.email,
                role_id=str(invitation.role_id),
                status=InvitationStatusType(invitation.status.value),
                expires_at=invitation.expires_at,
                accepted_at=invitation.accepted_at,
                created_at=invitation.created_at,
            )

