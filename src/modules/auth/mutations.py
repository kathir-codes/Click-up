import strawberry

from src.modules.auth.service import (
    sign_up,
    confirm_sign_up,
    resend_confirmation_code,
    sign_in,
    refresh_tokens,
)


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
        return sign_up(name=name, email=email, password=password)

    @strawberry.mutation
    def confirm_sign_up(
        self,
        email: str,
        confirmation_code: str,
    ) -> str:
        return confirm_sign_up(
            email=email,
            confirmation_code=confirmation_code,
        )

    @strawberry.mutation
    def resend_confirmation_code(self, email: str) -> str:
        return resend_confirmation_code(email=email)

    @strawberry.mutation
    def sign_in(self, email: str, password: str) -> SignInResponse:
        result = sign_in(email=email, password=password)

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
        result = refresh_tokens(refresh_token=refresh_token)

        return SignInResponse(
            message="Tokens refreshed successfully.",
            access_token=result["AccessToken"],
            id_token=result["IdToken"],
            refresh_token=result.get("RefreshToken"),
            expires_in=result["ExpiresIn"],
            token_type=result["TokenType"],
        )