from sqlalchemy import select
from sqlalchemy.orm import Session

from src.models.user import User, UserProfile


def create_or_update_user_profile(
    session: Session,
    cognito_sub: str,
    name: str,
    email: str,
) -> UserProfile:
    """Create a new user and profile. Reject existing users."""

    try:
        # 1. Check whether the Cognito user already exists.
        user = session.scalar(
            select(User).where(User.cognito_sub == cognito_sub)
        )

        if user is not None:
            raise ValueError("User already exists.")

        # 2. Check whether the email is already registered.
        existing_email = session.scalar(
            select(User).where(User.email == email)
        )

        if existing_email is not None:
            raise ValueError("Email is already registered.")

        # 3. Create the user.
        user = User(
            cognito_sub=cognito_sub,
            name=name,
            email=email,
        )
        session.add(user)
        session.flush()

        # 4. Create the user's profile.
        profile = UserProfile(
            user_id=user.user_id,
            name=name,
            email=email,
        )
        session.add(profile)

        # 5. Save both records.
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
    statement = (
        select(UserProfile)
        .join(User, User.user_id == UserProfile.user_id)
        .where(User.cognito_sub == cognito_sub)
    )

    return session.scalar(statement)


def update_user_profile(
    session: Session,
    cognito_sub: str,
    name: str | None = None,
    bio: str | None = None,
) -> UserProfile | None:
    try:
        profile = get_user_profile(
            session=session,
            cognito_sub=cognito_sub,
        )

        if profile is None:
            return None

        if name is not None:
            profile.name = name

        if bio is not None:
            profile.bio = bio

        session.commit()
        session.refresh(profile)

        return profile

    except Exception:
        session.rollback()
        raise