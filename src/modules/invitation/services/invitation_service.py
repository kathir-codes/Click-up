import hashlib
import secrets
from datetime import UTC, datetime, timedelta
from uuid import UUID

from sqlalchemy.orm import Session

from src.common.permissions import Permission
from src.models.invitation import Invitation, InvitationStatus
from src.modules.authorization.decorators import require_workspace_permission
from src.modules.invitation.repositories import invitation_repository as repository
from src.modules.workspace.repositories import workspace_repository

# -----------------------------
# CREATE WORKSPACE INVITATION
# -----------------------------

@require_workspace_permission(Permission.INVITE_MEMBER)
def create_workspace_invitation(
    session: Session,
    workspace_id: UUID,
    user_id: UUID,
    email: str,
    role_name: str,
):
    try:
        role = workspace_repository.get_system_role_by_name(
            session=session,
            role_name=role_name,
        )

        if role is None:
            raise ValueError("Role not found in this workspace.")

        token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        expires_at = datetime.now(UTC) + timedelta(days=7)

        invitation = repository.create_invitation(
            session=session,
            workspace_id=workspace_id,
            invited_by=user_id,
            email=email,
            role_id=role.role_id,
            token_hash=token_hash,
            expires_at=expires_at,
        )

        session.commit()
        session.refresh(invitation)

        return invitation, token

    except Exception:
        session.rollback()
        raise


# -----------------------------
# GET WORKSPACE INVITATIONS
# -----------------------------

@require_workspace_permission(Permission.VIEW_INVITATIONS)
def get_workspace_invitations(
    session: Session,
    workspace_id: UUID,
    user_id: UUID,
):
    return repository.get_workspace_invitations(
        session=session,
        workspace_id=workspace_id,
    )

# -----------------------------
# GET USER INVITATIONS
# -----------------------------

def get_user_invitations(
    session: Session,
    email: str,
):
    return repository.get_user_invitations(
        session=session,
        email=email,
    )


# -----------------------------
# ACCEPT WORKSPACE INVITATION
# -----------------------------

def accept_workspace_invitation(
    session: Session,
    token: str,
    user_id: UUID,
    email: str,
):
    try:
        token_hash = hashlib.sha256(token.encode()).hexdigest()

        invitation = repository.get_invitation_by_token_hash(
            session=session,
            token_hash=token_hash,
        )

        if invitation is None:
            raise ValueError("Invalid invitation.")

        if invitation.status != InvitationStatus.PENDING:
            raise ValueError("Invitation is no longer pending.")

        if invitation.expires_at <= datetime.now(UTC):
            repository.update_invitation_status(
                invitation=invitation,
                status=InvitationStatus.EXPIRED,
            )
            session.commit()
            raise ValueError("Invitation has expired.")

        if invitation.email.lower() != email.lower():
            raise ValueError(
                "This invitation belongs to a different email address."
            )

        existing_member = workspace_repository.get_workspace_member(
            session=session,
            workspace_id=invitation.workspace_id,
            user_id=user_id,
        )

        if existing_member is not None:
            raise ValueError("User is already a member of this workspace.")

        workspace_repository.create_workspace_member(
            session=session,
            workspace_id=invitation.workspace_id,
            user_id=user_id,
            role_id=invitation.role_id,
        )

        repository.update_invitation_status(
            invitation=invitation,
            status=InvitationStatus.ACCEPTED,
        )

        session.commit()
        session.refresh(invitation)

        return invitation

    except Exception:
        session.rollback()
        raise


# -----------------------------
# RESEND WORKSPACE INVITATION
# -----------------------------

@require_workspace_permission(Permission.RESEND_INVITATION)
def resend_workspace_invitation(
    session: Session,
    invitation_id: UUID,
    workspace_id: UUID,
    user_id: UUID,
):
    try:
        invitation = session.get(Invitation, invitation_id)

        if invitation is None:
            raise ValueError("Invitation not found.")

        if invitation.workspace_id != workspace_id:
            raise ValueError("Invitation does not belong to this workspace.")

        if invitation.status != InvitationStatus.PENDING:
            raise ValueError("Only pending invitations can be resent.")

        if invitation.expires_at <= datetime.now(UTC):
            repository.update_invitation_status(
                invitation=invitation,
                status=InvitationStatus.EXPIRED,
            )
            session.commit()
            raise ValueError("Invitation has expired.")

        token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        expires_at = datetime.now(UTC) + timedelta(days=7)

        repository.update_invitation_token(
            invitation=invitation,
            token_hash=token_hash,
            expires_at=expires_at,
        )

        session.commit()
        session.refresh(invitation)

        return invitation, token

    except Exception:
        session.rollback()
        raise


# -----------------------------
# CANCEL WORKSPACE INVITATION
# -----------------------------

@require_workspace_permission(Permission.CANCEL_INVITATION)
def cancel_workspace_invitation(
    session: Session,
    invitation_id: UUID,
    workspace_id: UUID,
    user_id: UUID,
):
    try:
        invitation = session.get(Invitation, invitation_id)

        if invitation is None:
            raise ValueError("Invitation not found.")

        if invitation.workspace_id != workspace_id:
            raise ValueError("Invitation does not belong to this workspace.")

        if invitation.status != InvitationStatus.PENDING:
            raise ValueError("Only pending invitations can be cancelled.")

        repository.update_invitation_status(
            invitation=invitation,
            status=InvitationStatus.CANCELLED,
        )

        session.commit()
        session.refresh(invitation)

        return invitation

    except Exception:
        session.rollback()
        raise


# -----------------------------
# DECLINE WORKSPACE INVITATION
# -----------------------------

def decline_workspace_invitation(
    session: Session,
    token: str,
    user_id: UUID,
    email: str,
):
    try:
        if user_id is None:
            raise ValueError("Authenticated user not found.")

        token_hash = hashlib.sha256(token.encode()).hexdigest()

        invitation = repository.get_invitation_by_token_hash(
            session=session,
            token_hash=token_hash,
        )

        if invitation is None:
            raise ValueError("Invalid invitation.")

        if invitation.status != InvitationStatus.PENDING:
            raise ValueError("Invitation is no longer pending.")

        if invitation.expires_at <= datetime.now(UTC):
            repository.update_invitation_status(
                invitation=invitation,
                status=InvitationStatus.EXPIRED,
            )
            session.commit()
            raise ValueError("Invitation has expired.")

        if invitation.email.lower() != email.lower():
            raise ValueError(
                "This invitation belongs to a different email address."
            )

        repository.update_invitation_status(
            invitation=invitation,
            status=InvitationStatus.DECLINED,
        )

        session.commit()
        session.refresh(invitation)

        return invitation

    except Exception:
        session.rollback()
        raise
