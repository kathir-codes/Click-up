
from uuid import UUID

import strawberry

from src.core.database import SessionLocal
from src.core.dependencies import get_current_user_sub
from src.modules.invitation.services import get_workspace_invitations
from src.modules.invitation.types import InvitationStatusType, InvitationType
from src.modules.user.services import get_profile


@strawberry.type
class InvitationQuery:

    @strawberry.field
    def workspace_invitations(
        self,
        info: strawberry.Info,
        workspace_id: str,
    ) -> list[InvitationType]:

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

            invitations = get_workspace_invitations(
                session=session,
                workspace_id=workspace_uuid,
                user_id=profile.user_id,
            )

            return [
                InvitationType(
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
                for invitation in invitations
            ]
