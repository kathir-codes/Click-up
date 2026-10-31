from src.core.cognito import (
    cognito,
    COGNITO_USER_POOL_ID,
    COGNITO_APP_CLIENT_ID,
    COGNITO_APP_CLIENT_SECRET,
    get_client_params,
    get_secret_hash,
)
from src.core.database import SessionLocal
from src.modules.user.service import sync_user_profile


def sign_up(name: str, email: str, password: str):
    username = email.strip().lower()

    params = {
        **get_client_params(username),
        "Username": username,
        "Password": password,
        "UserAttributes": [
            {"Name": "name", "Value": name.strip()},
            {"Name": "email", "Value": username},
        ],
    }

    cognito.sign_up(**params)

    return "Signup successful. Check your email for a verification code."


def confirm_sign_up(email: str, confirmation_code: str):
    username = email.strip().lower()

    cognito.confirm_sign_up(
        **get_client_params(username),
        Username=username,
        ConfirmationCode=confirmation_code,
    )

    user_response = cognito.admin_get_user(
        UserPoolId=COGNITO_USER_POOL_ID,
        Username=username,
    )

    attributes = {
        item["Name"]: item["Value"]
        for item in user_response.get("UserAttributes", [])
    }

    cognito_sub = attributes.get("sub")
    name = attributes.get("name")
    verified_email = attributes.get("email", username)

    if not cognito_sub or not name:
        raise ValueError("Cognito user ID or name was not found.")

    if attributes.get("email_verified") != "true":
        raise ValueError("Cognito has not verified this email.")

    with SessionLocal() as session:
        sync_user_profile(
            session=session,
            cognito_sub=cognito_sub,
            name=name,
            email=verified_email,
        )

    return "Email confirmed and user profile saved successfully."


def resend_confirmation_code(email: str):
    username = email.strip().lower()

    cognito.resend_confirmation_code(
        **get_client_params(username),
        Username=username,
    )

    return "A new verification code has been requested."


def sign_in(email: str, password: str):
    username = email.strip().lower()

    auth_parameters = {
        "USERNAME": username,
        "PASSWORD": password,
    }

    if COGNITO_APP_CLIENT_SECRET:
        auth_parameters["SECRET_HASH"] = get_secret_hash(username)

    response = cognito.initiate_auth(
        ClientId=COGNITO_APP_CLIENT_ID,
        AuthFlow="USER_PASSWORD_AUTH",
        AuthParameters=auth_parameters,
    )

    result = response.get("AuthenticationResult")

    if not result:
        raise ValueError("Additional authentication is required.")

    return result


def refresh_tokens(refresh_token: str):
    params = {
        "RefreshToken": refresh_token,
        "ClientId": COGNITO_APP_CLIENT_ID,
    }

    if COGNITO_APP_CLIENT_SECRET:
        params["ClientSecret"] = COGNITO_APP_CLIENT_SECRET

    response = cognito.get_tokens_from_refresh_token(**params)

    return response["AuthenticationResult"]