
from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy import func
from sqlalchemy.orm import Session

from src.models.invitation import Invitation, InvitationStatus


def create_invitation(
    session: Session,
    workspace_id: UUID,
    invited_by: UUID,
    email: str,
    role_id: UUID,
    token_hash: str,
    expires_at: datetime,
):
    invitation = Invitation(
        workspace_id=workspace_id,
        invited_by=invited_by,
        email=email,
        role_id=role_id,
        token_hash=token_hash,
        expires_at=expires_at,
    )

    session.add(invitation)

    return invitation


def get_invitation_by_token_hash(
    session: Session,
    token_hash: str,
) -> Invitation | None:
    return (
        session.query(Invitation)
        .filter(Invitation.token_hash == token_hash)
        .first()
    )


def get_workspace_invitations(
    session: Session,
    workspace_id: UUID,
) -> list[Invitation]:
    return (
        session.query(Invitation)
        .filter(Invitation.workspace_id == workspace_id)
        .order_by(Invitation.created_at.desc())
        .all()
    )


def get_user_invitations(
    session: Session,
    email: str,
) -> list[Invitation]:
    return (
        session.query(Invitation)
        .filter(func.lower(Invitation.email) == email.lower())
        .order_by(Invitation.created_at.desc())
        .all()
    )


def update_invitation_status(
    session: Session,
    invitation: Invitation,
    status: InvitationStatus,
):
    invitation.status = status

    if status == InvitationStatus.ACCEPTED:
        invitation.accepted_at = datetime.now(timezone.utc)

    return invitation

# This function updates the existing invitation's token hash and expiry date.
def update_invitation_token(
    session: Session,
    invitation: Invitation,
    token_hash: str,
    expires_at: datetime,
):
    invitation.token_hash = token_hash
    invitation.expires_at = expires_at

    return invitation