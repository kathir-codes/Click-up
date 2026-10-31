from sqlalchemy.orm import Session

from src.modules.user.repository import (
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
    # Business rule: required user details must exist.
    if not cognito_sub or not cognito_sub.strip():
        raise ValueError("Cognito user ID is required.")

    if not name or not name.strip():
        raise ValueError("Name is required.")

    if not email or not email.strip():
        raise ValueError("Email is required.")

    # Normalize data before saving.
    return  create_or_update_user_profile(
        session=session,
        cognito_sub=cognito_sub.strip(),
        name=name.strip(),
        email=email.strip().lower(),
    )


def get_profile(session: Session, cognito_sub: str):
    # Business rule: only a valid Cognito identity can be looked up.
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
    # Business rule: validate profile updates.
    if not cognito_sub or not cognito_sub.strip():
        raise ValueError("Cognito user ID is required.")

    if name is not None and not name.strip():
        raise ValueError("Name cannot be empty.")

    if bio is not None and len(bio) > 500:
        raise ValueError("Bio cannot exceed 500 characters.")

    return update_user_profile(
        session=session,
        cognito_sub=cognito_sub.strip(),
        name=name.strip() if name is not None else None,
        bio=bio.strip() if bio is not None else None,
    )