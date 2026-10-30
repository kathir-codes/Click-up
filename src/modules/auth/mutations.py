
import strawberry

from src.core.cognito import (
    cognito,
    COGNITO_USER_POOL_ID,
    COGNITO_APP_CLIENT_ID,
    COGNITO_APP_CLIENT_SECRET,
    get_client_params,
    get_secret_hash,
)
from src.core.database import SessionLocal
from src.database.user_operations import create_or_update_user_profile
from src.core.jwt import validate_id_token

@strawberry.type
class SignInResponse:
    message: str
    access_token: str
    id_token: str
    refresh_token: str | None
    expires_in: int
    token_type: str


@strawberry.type
class AuthMutation:

    @strawberry.mutation
    def sign_up(self, name: str, email: str, password: str) -> str:
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



    @strawberry.mutation
    def confirm_sign_up(
        self,
        email: str,
        confirmation_code: str,
    ) -> str:
        username = email.strip().lower()

        # Step 1: Confirm the signup using Cognito.
        cognito.confirm_sign_up(
            **get_client_params(username),
            Username=username,
            ConfirmationCode=confirmation_code,
        )

        # Step 2: Get the confirmed user's details from Cognito.
        user_response = cognito.admin_get_user(
            UserPoolId=COGNITO_USER_POOL_ID,
            Username=username,
        )

        # Step 3: Read the Cognito user attributes.
        attributes = {
            item["Name"]: item["Value"]
            for item in user_response.get("UserAttributes", [])
        }

        cognito_sub = attributes.get("sub")
        name = attributes.get("name")
        verified_email = attributes.get("email", username)
        email_verified = attributes.get("email_verified") == "true"

        # Step 4: Validate the user details.
        if not cognito_sub or not name:
            raise ValueError("Cognito user ID or name was not found.")

        if not email_verified:
            raise ValueError("Cognito has not verified this email.")

        # Step 5: Save the user and profile to Supabase.
        with SessionLocal() as session:
            create_or_update_user_profile(
                session=session,
                cognito_sub=cognito_sub,
                name=name,
                email=verified_email,
            )

        return "Email confirmed and user profile saved successfully."



    @strawberry.mutation
    def resend_confirmation_code(self, email: str) -> str:
        username = email.strip().lower()

        cognito.resend_confirmation_code(
            **get_client_params(username),
            Username=username,
        )

        return "A new verification code has been requested."

    @strawberry.mutation
    def sign_in(self, email: str, password: str) -> SignInResponse:
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

        return SignInResponse(
            message="Login successful.",
            access_token=result["AccessToken"],
            id_token=result["IdToken"],
            refresh_token=result.get("RefreshToken"),
            expires_in=result["ExpiresIn"],
            token_type=result["TokenType"],
        )

    @strawberry.mutation
    def refresh_tokens(self, refresh_token: str) -> SignInResponse:
        params = {
            "RefreshToken": refresh_token,
            "ClientId": COGNITO_APP_CLIENT_ID,
        }

        if COGNITO_APP_CLIENT_SECRET:
            params["ClientSecret"] = COGNITO_APP_CLIENT_SECRET

        response = cognito.get_tokens_from_refresh_token(**params)
        result = response["AuthenticationResult"]

        return SignInResponse(
            message="Tokens refreshed successfully.",
            access_token=result["AccessToken"],
            id_token=result["IdToken"],
            refresh_token=result.get("RefreshToken"),
            expires_in=result["ExpiresIn"],
            token_type=result["TokenType"],
        )
