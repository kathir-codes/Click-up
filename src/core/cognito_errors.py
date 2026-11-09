import logging

from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


def handle_cognito_error(error: ClientError) -> None:
    error_code = error.response.get("Error", {}).get("Code")
    error_message = error.response.get("Error", {}).get("Message")

    error_messages = {
        "ExpiredCodeException": "Confirmation code has expired. Please request a new code.",
        "CodeMismatchException": "Invalid confirmation code.",
        "UsernameExistsException": "An account with this email already exists.",
        "UserNotFoundException": "User not found.",
        "NotAuthorizedException": "Invalid credentials or authorization failed.",
        "InvalidPasswordException": "Password does not meet the password policy.",
        "LimitExceededException": "Too many attempts. Please try again later.",
        "UserNotConfirmedException": "Please verify your email before signing in.",
        "PasswordResetRequiredException": "Password reset is required before signing in.",
        "UserLambdaValidationException": "The supplied user information could not be accepted.",
    }

    message = error_messages.get(error_code)

    if message:
        logger.warning(
            "Cognito application error | Code=%s | Message=%s",
            error_code,
            error_message,
        )
        raise ValueError(message) from error

    logger.error(
        "Unexpected Cognito error | Code=%s | Message=%s",
        error_code,
        error_message,
        exc_info=(
            type(error),
            error,
            error.__traceback__,
        ),
    )

    raise RuntimeError("Unexpected Cognito service error.") from error
