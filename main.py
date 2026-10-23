import os  #use it to read configuration values from environment variables.
import hashlib
import hmac
import base64

import boto3 # used to communicate with aws service.
import strawberry # the Python library you use to create a GraphQL API. 
from dotenv import load_dotenv
from fastapi import FastAPI, Request, HTTPException
from strawberry.fastapi import GraphQLRouter # the integration between Strawberry GraphQL and FastAPI. # connects your GraphQL schema to a FastAPI route.

from database import (
    create_user_profile,
    get_user_profile,
)

load_dotenv()


# ---------------------- AWS Cognito Configuration ----------------------

AWS_REGION = os.getenv("AWS_REGION")
COGNITO_USER_POOL_ID = os.getenv("COGNITO_USER_POOL_ID")
COGNITO_APP_CLIENT_ID = os.getenv("COGNITO_APP_CLIENT_ID")
COGNITO_APP_CLIENT_SECRET = os.getenv("COGNITO_APP_CLIENT_SECRET")

if not AWS_REGION or not COGNITO_USER_POOL_ID or not COGNITO_APP_CLIENT_ID:
    raise ValueError("Cognito configuration is missing from .env")

cognito = boto3.client(
    "cognito-idp",
    region_name=AWS_REGION,
)


# ---------------------- Cognito Secret Hash ----------------------

def get_secret_hash(username: str) -> str:
    if not COGNITO_APP_CLIENT_SECRET:
        raise ValueError("Cognito app client secret is missing from .env")

    message = username + COGNITO_APP_CLIENT_ID

    digest = hmac.new(
        COGNITO_APP_CLIENT_SECRET.encode("utf-8"),
        message.encode("utf-8"),
        hashlib.sha256,
    ).digest()

    return base64.b64encode(digest).decode("utf-8")


def get_client_params(username: str) -> dict:
    params = {
        "ClientId": COGNITO_APP_CLIENT_ID,
    }

    if COGNITO_APP_CLIENT_SECRET:
        params["SecretHash"] = get_secret_hash(username)

    return params


# ---------------------- GraphQL Mutations ----------------------
@strawberry.type
class SignInResponse:
    message: str
    access_token: str #Token used to access protected APIs
    id_token: str #Token containing information about the logged-in use
    refresh_token: str | None
    expires_in: int #How long the access token is valid, in seconds
    token_type: str #The token type returned by Cognito

   
@strawberry.type
class Mutation:
# ---------------------Sign-up------------------------------------
    @strawberry.mutation
    def sign_up(
        self,
        name: str,
        email: str,
        password: str,
    ) -> str:
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

        params = {
            **get_client_params(username),
            "ConfirmationCode": confirmation_code.strip(),
            "Username": username,
        }

        # Step 1: Confirm the email using Cognito
        cognito.confirm_sign_up(**params)

        # Step 2: Get the user's details from Cognito
        user_response = cognito.admin_get_user(
            UserPoolId=COGNITO_USER_POOL_ID,
            Username=username,
        )   

        attributes = {
            attr["Name"]: attr["Value"]
            for attr in user_response.get("UserAttributes", [])
        }

        user_id = attributes.get("sub")
        user_name = attributes.get("name")
        verified_email = attributes.get("email", username)
        email_verified = attributes.get("email_verified") == "true"

        # Step 3: Check the required user details
        if not user_id or not user_name:
            raise ValueError("Cognito user ID or name was not found.")

        if not email_verified:
            raise ValueError("Cognito has not verified this email.")

        # Step 4: Check whether the profile already exists in Supabase
        existing_profile = get_user_profile(user_id)

        if existing_profile:
            return "Email confirmed. User profile already exists."
        
        # Step 5: Save the user profile in Supabase
        create_user_profile(
            user_id=user_id,
            name=user_name,
            email=verified_email,
            email_verified=True,
        )

        return "Email confirmed and profile saved successfully."


    @strawberry.mutation
    def resend_confirmation_code(self, email: str) -> str:
        username = email.strip().lower()

        params = {
            **get_client_params(username),
            "Username": username,
        }

        cognito.resend_confirmation_code(**params)

        return "A new verification code has been requested."
# ----------------------sign-in------------------------------


    
    
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

# ---------------------- Cognito Access Token Validation ----------------------

import jwt
from jwt import PyJWKClient

COGNITO_ISSUER = (
    f"https://cognito-idp.{AWS_REGION}.amazonaws.com/{COGNITO_USER_POOL_ID}"
)

JWKS_URL = f"{COGNITO_ISSUER}/.well-known/jwks.json"

jwks_client = PyJWKClient(JWKS_URL)#key-fetching helper


def validate_access_token(token: str) -> dict:
    signing_key = jwks_client.get_signing_key_from_jwt(token)

    claims = jwt.decode(
        token,
        signing_key.key,
        algorithms=["RS256"],
        issuer=COGNITO_ISSUER,
        options={
            "require": ["exp", "iat", "iss", "sub", "token_use", "client_id"],
        },
        audience=None,
    )

    if claims.get("token_use") != "access":
        raise ValueError("Access token required.")

    if claims.get("client_id") != COGNITO_APP_CLIENT_ID:
        raise ValueError("Token was issued to an unexpected app client.")

    return claims


        

# ---------------------- GraphQL Query ----------------------
@strawberry.type
class UserProfileType:
    id: str
    name: str
    email: str
    email_verified: bool

@strawberry.type
class Query:

    @strawberry.field
    def my_profile(self, info: strawberry.Info) -> UserProfileType:
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

        user_id = claims["sub"]

        profile = get_user_profile(user_id)

        if profile is None:
            raise ValueError("User profile not found.")

        return UserProfileType(
        id=str(profile.id),
        name=profile.name,
        email=profile.email,
        email_verified=profile.email_verified,
        )   



# ---------------------- GraphQL Schema ----------------------

schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
)

# ---------------------- GraphQL Request Context ----------------------

async def get_context(request: Request) -> dict:
    return {"request": request}

# ---------------------- FastAPI Application ----------------------

graphql_app = GraphQLRouter(
    schema,
    context_getter=get_context,
)

app = FastAPI()
app.include_router(graphql_app, prefix="/graphql")