
import jwt
from jwt import PyJWKClient

from src.core.cognito import (
    AWS_REGION,
    COGNITO_USER_POOL_ID,
    COGNITO_APP_CLIENT_ID,
)

COGNITO_ISSUER = (
    f"https://cognito-idp.{AWS_REGION}.amazonaws.com/"
    f"{COGNITO_USER_POOL_ID}"
)

JWKS_URL = f"{COGNITO_ISSUER}/.well-known/jwks.json"

jwks_client = PyJWKClient(JWKS_URL)


def validate_access_token(token: str) -> dict:
    signing_key = jwks_client.get_signing_key_from_jwt(token)

    claims = jwt.decode(
        token,
        signing_key.key,
        algorithms=["RS256"],
        issuer=COGNITO_ISSUER,
        options={
            "require": [
                "exp",
                "iat",
                "iss",
                "sub",
                "token_use",
                "client_id",
            ],
        },
        audience=None,
    )

    if claims.get("token_use") != "access":
        raise ValueError("Access token required.")

    if claims.get("client_id") != COGNITO_APP_CLIENT_ID:
        raise ValueError("Token was issued to an unexpected app client.")

    return claims



# def validate_id_token(token: str) -> dict:
#     signing_key = jwks_client.get_signing_key_from_jwt(token)

#     claims = jwt.decode(
#         token,
#         signing_key.key,
#         algorithms=["RS256"],
#         issuer=COGNITO_ISSUER,
#         audience=COGNITO_APP_CLIENT_ID,
#         options={
#             "require": [
#                 "exp",
#                 "iat",
#                 "iss",
#                 "sub",
#                 "token_use",
#                 "aud",
#             ],
#         },
#     )

#     if claims.get("token_use") != "id":
#         raise ValueError("ID token required.")

#     return claims
