import enum
from datetime import datetime

import strawberry


@strawberry.enum
class InvitationStatusType(enum.Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    EXPIRED = "EXPIRED"
    CANCELLED = "CANCELLED"
    DECLINED = "DECLINED"


@strawberry.type
class InvitationType:
    invitation_id: str
    workspace_id: str
    invited_by: str
    email: str
    role_id: str
    status: InvitationStatusType
    expires_at: datetime
    accepted_at: datetime | None
    created_at: datetime
    token: str | None = None
