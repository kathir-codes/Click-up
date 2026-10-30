import strawberry


@strawberry.type
class UserProfileType:
    id: str
    name: str
    email: str

    