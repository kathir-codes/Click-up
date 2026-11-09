from datetime import datetime

import strawberry


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
