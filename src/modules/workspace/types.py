
from datetime import datetime

import strawberry


# ==============================
# Output DTOs
# ==============================

@strawberry.type
class WorkspaceType:
    workspace_id: str
    name: str
    slug: str
    description: str | None


@strawberry.type
class WorkspaceMemberType:
    user_id: str
    name: str
    email: str
    role_name: str
    joined_at: datetime


# ==============================
# Input DTOs
# ==============================

@strawberry.input
class CreateWorkspaceInput:
    name: str
    slug: str
    description: str | None = None


@strawberry.input
class UpdateWorkspaceInput:
    name: str | None = None
    slug: str | None = None
    description: str | None = None
