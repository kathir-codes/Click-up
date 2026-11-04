
import strawberry

from uuid import UUID

from src.core.database import SessionLocal
from src.core.dependencies import get_current_user_sub
from src.modules.user.service import get_profile
from src.modules.authorization.service import check_workspace_permission
from src.modules.invitation.service import get_workspace_invitations
from src.modules.invitation.types import InvitationType, InvitationStatusType


@strawberry.type
class InvitationQuery:

    # -----------------------------
    # GET WORKSPACE INVITATIONS
    # -----------------------------

    @strawberry.field
    def workspace_invitations(
        self,
        info: strawberry.Info,
        workspace_id: str,
    ) -> list[InvitationType]:

        # 1. Get logged-in user's Cognito sub
        cognito_sub = get_current_user_sub(info)

        try:
            workspace_uuid = UUID(workspace_id)
        except ValueError:
            raise ValueError("Invalid workspace ID.")

        with SessionLocal() as session:

            # 2. Get logged-in user's profile
            profile = get_profile(
                session=session,
                cognito_sub=cognito_sub,
            )

            if profile is None:
                raise ValueError("User profile not found.")

            # 3. Check VIEW_INVITATIONS permission
            has_permission = check_workspace_permission(
                session=session,
                workspace_id=workspace_uuid,
                user_id=profile.user_id,
                permission_name="VIEW_INVITATIONS",
            )

            if not has_permission:
                raise ValueError(
                    "You don't have permission to view workspace invitations."
                )

            # 4. Get workspace invitations
            invitations = get_workspace_invitations(
                session=session,
                workspace_id=workspace_uuid,
            )

            # 5. Return invitation details
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
