import strawberry


@strawberry.type
class UserProfileType:
    user_id: str
    name: str
    email: str
    bio: str | None
    is_active: bool