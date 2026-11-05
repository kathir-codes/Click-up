
import strawberry

from src.core.database import SessionLocal
from src.modules.user.types import UserProfileType
from src.core.dependencies import get_current_user_sub  
from src.modules.user.services import update_profile
@strawberry.type
class UserMutation:

    @strawberry.mutation
    def update_my_profile(
        self,
        info: strawberry.Info,
        name: str | None = None,
        bio: str | None = None,
    ) -> UserProfileType:

        cognito_sub = get_current_user_sub(info)

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
                email=profile.user.email,
                bio=profile.bio,
                created_at=profile.created_at,
                updated_at=profile.updated_at,
            )
    