import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy.orm import Session

from src.models.invitation import Invitation, InvitationStatus
from src.modules.invitation.repositories import invitation_repository as repository
from src.modules.workspace.repositories import workspace_repository


# -----------------------------
# CREATE WORKSPACE INVITATION
# -----------------------------
def create_workspace_invitation(
    session: Session,
    workspace_id: UUID,
    invited_by: UUID,
    email: str,
    role_name: str,
):
    try:
        # 1. Find role using workspace_id and role_name
        role = workspace_repository.get_role_by_name(
            session=session,
            workspace_id=workspace_id,
            role_name=role_name,
        )

        if role is None:
            raise ValueError("Role not found in this workspace.")

        # 2. Generate a secure invitation token
        token = secrets.token_urlsafe(32)

        # 3. Generate token hash
        token_hash = hashlib.sha256(token.encode()).hexdigest()

        # 4. Set invitation expiry (7 days)
        expires_at = datetime.now(timezone.utc) + timedelta(days=7)

        # 5. Create invitation record
        invitation = repository.create_invitation(
            session=session,
            workspace_id=workspace_id,
            invited_by=invited_by,
            email=email,
            role_id=role.role_id,
            token_hash=token_hash,
            expires_at=expires_at,
        )

        # 6. Commit invitation
        session.commit()
        session.refresh(invitation)

        return invitation, token

    except Exception:
        session.rollback()
        raise


# -----------------------------
# GET WORKSPACE INVITATIONS
# -----------------------------
def get_workspace_invitations(
    session: Session,
    workspace_id: UUID,
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
        # 1. Generate token hash
        token_hash = hashlib.sha256(token.encode()).hexdigest()

        # 2. Find invitation
        invitation = repository.get_invitation_by_token_hash(
            session=session,
            token_hash=token_hash,
        )

        if invitation is None:
            raise ValueError("Invalid invitation.")

        # 3. Check invitation status
        if invitation.status != InvitationStatus.PENDING:
            raise ValueError("Invitation is no longer pending.")

        # 4. Check invitation expiry
        if invitation.expires_at <= datetime.now(timezone.utc):
            repository.update_invitation_status(
                invitation=invitation,
                status=InvitationStatus.EXPIRED,
            )
            session.commit()
            raise ValueError("Invitation has expired.")

        # 5. Verify invited email
        if invitation.email.lower() != email.lower():
            raise ValueError("This invitation belongs to a different email address.")

        # 6. Check existing workspace membership
        existing_member = workspace_repository.get_workspace_member(
            session=session,
            workspace_id=invitation.workspace_id,
            user_id=user_id,
        )

        if existing_member is not None:
            raise ValueError("User is already a member of this workspace.")

        # 7. Add user to workspace with invited role
        workspace_repository.create_workspace_member(
            session=session,
            workspace_id=invitation.workspace_id,
            user_id=user_id,
            role_id=invitation.role_id,
        )

        # 8. Update invitation status
        repository.update_invitation_status(
            invitation=invitation,
            status=InvitationStatus.ACCEPTED,
        )

        # 9. Commit changes
        session.commit()
        session.refresh(invitation)

        return invitation

    except Exception:
        session.rollback()
        raise


# -----------------------------
# RESEND WORKSPACE INVITATION
# -----------------------------
def resend_workspace_invitation(
    session: Session,
    invitation_id: UUID,
):
    try:
        # 1. Find invitation
        invitation = session.get(
            Invitation,
            invitation_id,
        )

        if invitation is None:
            raise ValueError("Invitation not found.")

        # 2. Check invitation status
        if invitation.status != InvitationStatus.PENDING:
            raise ValueError("Only pending invitations can be resent.")

        # 3. Check invitation expiry
        if invitation.expires_at <= datetime.now(timezone.utc):
            repository.update_invitation_status(
                invitation=invitation,
                status=InvitationStatus.EXPIRED,
            )
            session.commit()
            raise ValueError("Invitation has expired.")

        # 4. Generate a new secure invitation token
        token = secrets.token_urlsafe(32)

        # 5. Generate token hash
        token_hash = hashlib.sha256(token.encode()).hexdigest()

        # 6. Set invitation expiry (7 days)
        expires_at = datetime.now(timezone.utc) + timedelta(days=7)

        # 7. Update existing invitation
        repository.update_invitation_token(
            invitation=invitation,
            token_hash=token_hash,
            expires_at=expires_at,
        )

        # 8. Commit changes
        session.commit()
        session.refresh(invitation)

        return invitation, token

    except Exception:
        session.rollback()
        raise


# -----------------------------
# CANCEL WORKSPACE INVITATION
# -----------------------------
def cancel_workspace_invitation(
    session: Session,
    invitation_id: UUID,
):
    try:
        # 1. Find invitation
        invitation = session.get(
            Invitation,
            invitation_id,
        )

        if invitation is None:
            raise ValueError("Invitation not found.")

        # 2. Check invitation status
        if invitation.status != InvitationStatus.PENDING:
            raise ValueError("Only pending invitations can be cancelled.")

        # 3. Update invitation status
        repository.update_invitation_status(
            invitation=invitation,
            status=InvitationStatus.CANCELLED,
        )

        # 4. Commit changes
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
        # 1. Generate token hash
        token_hash = hashlib.sha256(token.encode()).hexdigest()

        # 2. Find invitation
        invitation = repository.get_invitation_by_token_hash(
            session=session,
            token_hash=token_hash,
        )

        if invitation is None:
            raise ValueError("Invalid invitation.")

        # 3. Check invitation status
        if invitation.status != InvitationStatus.PENDING:
            raise ValueError("Invitation is no longer pending.")

        # 4. Check invitation expiry
        if invitation.expires_at <= datetime.now(timezone.utc):
            repository.update_invitation_status(
                invitation=invitation,
                status=InvitationStatus.EXPIRED,
            )
            session.commit()
            raise ValueError("Invitation has expired.")

        # 5. Verify invited email
        if invitation.email.lower() != email.lower():
            raise ValueError("This invitation belongs to a different email address.")

        # 6. Verify the authenticated user
        if user_id is None:
            raise ValueError("Authenticated user not found.")

        # 7. Update invitation status
        repository.update_invitation_status(
            invitation=invitation,
            status=InvitationStatus.DECLINED,
        )

        # 8. Commit changes
        session.commit()
        session.refresh(invitation)

        return invitation

    except Exception:
        session.rollback()
        raise
