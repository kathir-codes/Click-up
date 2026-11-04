
import logging
import strawberry

from fastapi import Request
from strawberry.fastapi import GraphQLRouter
from strawberry.http import GraphQLHTTPResponse
from strawberry.types import ExecutionResult, ExecutionContext
from graphql import GraphQLError


logger = logging.getLogger(__name__)


def log_graphql_errors(
    errors: list[GraphQLError]
) -> None:
    for error in errors:
        original_error = error.original_error

        if isinstance(original_error, ValueError):
            logger.warning("Application error: %s", error.message)

        elif original_error is not None and not isinstance(
            original_error, GraphQLError
        ):
            logger.error(
                "Unexpected GraphQL error: %s",
                error.message,
                exc_info=(
                    type(original_error),
                    original_error,
                    original_error.__traceback__,
                ),
            )

        else:
            logger.warning("GraphQL error: %s", error.message)


class CustomSchema(strawberry.Schema):

    def process_errors(
        self,
        errors: list[GraphQLError],
        execution_context: ExecutionContext | None = None,
    ) -> None:
        log_graphql_errors(errors)


class CustomGraphQLRouter(GraphQLRouter):

    async def process_result(
        self,
        request: Request,
        result: ExecutionResult,
    ) -> GraphQLHTTPResponse:

        request_id = getattr(request.state, "request_id", "-")

        response: GraphQLHTTPResponse = {"data": result.data}

        if not result.errors:
            return response

        formatted_errors = []

        for error in result.errors:
            original_error = error.original_error

            if isinstance(original_error, ValueError):
                formatted_error = error.formatted.copy()
                formatted_error["message"] = str(original_error)

            elif original_error is not None and not isinstance(
                original_error, GraphQLError
            ):
                formatted_error = {
                    "message": "Internal server error",
                    "extensions": {"code": "INTERNAL_SERVER_ERROR"},
                }

            else:
                formatted_error = error.formatted.copy()

            formatted_error.setdefault("extensions", {})
            formatted_error["extensions"]["requestId"] = request_id

            formatted_errors.append(formatted_error)

        response["errors"] = formatted_errors

        return response
