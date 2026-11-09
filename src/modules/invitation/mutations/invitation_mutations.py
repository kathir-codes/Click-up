
from uuid import UUID

import strawberry

from src.core.database import SessionLocal
from src.core.dependencies import get_current_user_sub
from src.models.invitation import Invitation
from src.modules.invitation.services import (
    accept_workspace_invitation as accept_invitation_service,
    cancel_workspace_invitation,
    create_workspace_invitation,
    decline_workspace_invitation as decline_invitation_service,
    resend_workspace_invitation,
)
from src.modules.invitation.types import InvitationStatusType, InvitationType
from src.modules.user.services import get_profile


@strawberry.type
class InvitationMutation:

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

            invitation, token = create_workspace_invitation(
                session=session,
                workspace_id=workspace_uuid,
                user_id=profile.user_id,
                email=email,
                role_name=role_name,
            )

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

    @strawberry.mutation
    def accept_workspace_invitation(
        self,
        info: strawberry.Info,
        token: str,
    ) -> InvitationType:

        cognito_sub = get_current_user_sub(info)

        with SessionLocal() as session:
            profile = get_profile(
                session=session,
                cognito_sub=cognito_sub,
            )

            if profile is None:
                raise ValueError("User profile not found.")

            invitation = accept_invitation_service(
                session=session,
                token=token,
                user_id=profile.user_id,
                email=profile.user.email,
            )

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
            profile = get_profile(
                session=session,
                cognito_sub=cognito_sub,
            )

            if profile is None:
                raise ValueError("User profile not found.")

            invitation = session.get(Invitation, invitation_uuid)

            if invitation is None:
                raise ValueError("Invitation not found.")

            invitation, token = resend_workspace_invitation(
                session=session,
                invitation_id=invitation_uuid,
                workspace_id=invitation.workspace_id,
                user_id=profile.user_id,
            )

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
            profile = get_profile(
                session=session,
                cognito_sub=cognito_sub,
            )

            if profile is None:
                raise ValueError("User profile not found.")

            invitation = session.get(Invitation, invitation_uuid)

            if invitation is None:
                raise ValueError("Invitation not found.")

            invitation = cancel_workspace_invitation(
                session=session,
                invitation_id=invitation_uuid,
                workspace_id=invitation.workspace_id,
                user_id=profile.user_id,
            )

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

    @strawberry.mutation
    def decline_workspace_invitation(
        self,
        info: strawberry.Info,
        token: str,
    ) -> InvitationType:

        cognito_sub = get_current_user_sub(info)

        with SessionLocal() as session:
            profile = get_profile(
                session=session,
                cognito_sub=cognito_sub,
            )

            if profile is None:
                raise ValueError("User profile not found.")

            invitation = decline_invitation_service(
                session=session,
                token=token,
                user_id=profile.user_id,
                email=profile.user.email,
            )

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
