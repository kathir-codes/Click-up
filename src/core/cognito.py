
import os
import base64
import hashlib
import hmac

import boto3
from dotenv import load_dotenv

load_dotenv()

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
    params = {"ClientId": COGNITO_APP_CLIENT_ID}

    if COGNITO_APP_CLIENT_SECRET:
        params["SecretHash"] = get_secret_hash(username)

    return params