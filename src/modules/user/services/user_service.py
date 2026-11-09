from sqlalchemy.orm import Session

from src.modules.user.repositories import (
    create_or_update_user_profile,
    get_user_profile,
    update_user_profile,
)


def sync_user_profile(
    session: Session,
    cognito_sub: str,
    name: str,
    email: str,
):
    if not cognito_sub or not cognito_sub.strip():
        raise ValueError("Cognito user ID is required.")

    if not name or not name.strip():
        raise ValueError("Name is required.")

    if not email or not email.strip():
        raise ValueError("Email is required.")

    return create_or_update_user_profile(
        session=session,
        cognito_sub=cognito_sub.strip(),
        name=name.strip(),
        email=email.strip().lower(),
    )


def get_profile(session: Session, cognito_sub: str):
    if not cognito_sub or not cognito_sub.strip():
        raise ValueError("Cognito user ID is required.")

    return get_user_profile(
        session=session,
        cognito_sub=cognito_sub.strip(),
    )


def update_profile(
    session: Session,
    cognito_sub: str,
    name: str | None = None,
    bio: str | None = None,
):
    if not cognito_sub or not cognito_sub.strip():
        raise ValueError("Cognito user ID is required.")

    if name is not None and not name.strip():
        raise ValueError("Name cannot be empty.")

    if bio is not None and len(bio) > 255:
        raise ValueError("Bio cannot exceed 255 characters.")

    return update_user_profile(
        session=session,
        cognito_sub=cognito_sub.strip(),
        name=name.strip() if name is not None else None,
        bio=bio.strip() if bio is not None else None,
    )
