import strawberry

from src.core.database import SessionLocal
from src.core.jwt import validate_access_token
from src.modules.user.service import update_profile
from src.modules.user.types import UserProfileType


@strawberry.type
class UserMutation:

    @strawberry.mutation
    def update_my_profile(
        self,
        info: strawberry.Info,
        name: str | None = None,
        bio: str | None = None,
    ) -> UserProfileType:

        authorization = info.context["request"].headers.get("Authorization")

        if not authorization or not authorization.startswith("Bearer "):
            raise ValueError("Bearer token required.")

        token = authorization.split(" ", 1)[1].strip()

        if not token:
            raise ValueError("Access token is missing.")

        try:
            claims = validate_access_token(token)
        except Exception as exc:
            raise ValueError("Invalid or expired access token.") from exc

        cognito_sub = claims["sub"]

        with SessionLocal() as session:
            profile = update_profile(
                session=session,
                cognito_sub=cognito_sub,
                name=name,
                bio=bio,
            )

            if profile is None:
                raise ValueError("User profile not found.")

            return UserProfileType(
                user_id=str(profile.user_id),
                name=profile.name,
                email=profile.email,
                bio=profile.bio,
                is_active=profile.is_active if profile.is_active is not None else True,
            )