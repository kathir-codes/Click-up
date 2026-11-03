
import strawberry

from src.core.database import SessionLocal
from src.core.jwt import validate_access_token
from src.modules.user.service import get_profile
from src.modules.user.types import UserProfileType
from src.core.dependencies import get_current_user_sub

@strawberry.type
class UserQuery:

    @strawberry.field
    def my_profile(self, info: strawberry.Info) -> UserProfileType:
        cognito_sub =  get_current_user_sub(info)

        with SessionLocal() as session:
            profile = get_profile(
                session=session,
                cognito_sub=cognito_sub,
            )

            if profile is None:
                raise ValueError("User profile not found.")

            return UserProfileType(
                user_id=str(profile.user_id),
                name=profile.name,
                email=profile.user.email,
                bio=profile.bio,
                created_at=profile.created_at,
                updated_at=profile.updated_at,
            )

   