
from sqlalchemy import select
from sqlalchemy.orm import Session

from src.models.user import User, UserProfile


def create_or_update_user_profile(
    session: Session,
    cognito_sub: str,
    name: str,
    email: str,
) -> UserProfile:

 
    try:
        # 1. Find the user using Cognito's sub.
        user = session.scalar(
            select(User).where(User.cognito_sub == cognito_sub)
        )

        # 2. Create the user if it does not exist.
        if user is None:
            user = session.scalar(
                select(User).where(User.email == email)
            )

        if user is None:
            user = User(
                cognito_sub=cognito_sub,
                name=name,
                email=email,
            )
            session.add(user)
            session.flush()
        else:
            # Update the existing user's details.
            user.cognito_sub = cognito_sub
            user.name = name
            user.email = email
            session.flush()

        # 3. Find the profile linked to this user.
        profile = session.scalar(
            select(UserProfile).where(
                UserProfile.user_id == user.user_id
            )
        )

        # 4. Create or update the profile.
        if profile is None:
            profile = UserProfile(
                user_id=user.user_id,
                name=name,
                email=email,
            )
            session.add(profile)
        else:
            profile.name = name
            profile.email = email

        # 5. Save both records together.
        session.commit()
        session.refresh(profile)

        return profile

    except Exception:
        session.rollback()
        raise


def get_user_profile(
    session: Session,
    cognito_sub: str,
) -> UserProfile | None:
    """Find a user's profile using Cognito's sub."""

    statement = (
        select(UserProfile)
        .join(User, UserProfile.user_id == User.user_id)
        .where(User.cognito_sub == cognito_sub)
    )

    return session.scalar(statement)