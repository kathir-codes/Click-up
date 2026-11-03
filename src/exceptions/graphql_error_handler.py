
import logging
import strawberry

from fastapi import Request
from strawberry.fastapi import GraphQLRouter
from strawberry.http import GraphQLHTTPResponse
from strawberry.types import ExecutionResult
from graphql import GraphQLError
from strawberry.types.execution import ExecutionContext


logger = logging.getLogger(__name__)


def log_graphql_errors(
    errors: list[GraphQLError],
    execution_context: ExecutionContext | None = None,
) -> None:
    for error in errors:
        original_error = error.original_error

        if original_error is not None:
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
            logger.warning(
                "GraphQL error: %s",
                error.message,
            )


class CustomSchema(strawberry.Schema):

    def process_errors(
        self,
        errors: list[GraphQLError],
        execution_context: ExecutionContext | None = None,
    ) -> None:
        log_graphql_errors(errors, execution_context)


class CustomGraphQLRouter(GraphQLRouter):

    async def process_result(
        self,
        request: Request,
        result: ExecutionResult,
    ) -> GraphQLHTTPResponse:

        response: GraphQLHTTPResponse = {
            "data": result.data,
        }

        if result.errors:
            response["errors"] = []

            for error in result.errors:
                formatted_error = error.formatted.copy()
                original_error = error.original_error

                if original_error is not None:
                    if isinstance(original_error, ValueError):
                        formatted_error["message"] = str(original_error)
                    else:
                        formatted_error["message"] = (
                            "An unexpected error occurred."
                        )
                        formatted_error.pop("extensions", None)

                response["errors"].append(formatted_error)

        return response
