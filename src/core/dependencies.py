"""Authentication dependencies for GraphQL resolvers."""

from strawberry.types import Info

from src.core.jwt import validate_access_token


# -----------------------------
# GET CURRENT AUTHENTICATED USER
# -----------------------------
def get_current_user(info: Info) -> dict:
    """Validate the access token and return Cognito user claims."""

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

    return claims


# -----------------------------
# GET CURRENT USER COGNITO SUB
# -----------------------------
def get_current_user_sub(info: Info) -> str:
    """Return the authenticated user's Cognito sub."""

    claims = get_current_user(info)
    return claims["sub"]
