from datetime import datetime

import strawberry


@strawberry.type
class UserProfileType:
    user_id: str
    name: str
    email: str
    bio: str | None
    created_at: datetime
    updated_at: datetime
