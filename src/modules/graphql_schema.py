import logging
import strawberry
from src.exceptions.graphql_error_handler import CustomSchema
from graphql import GraphQLError
from strawberry.types.execution import ExecutionContext

from src.modules.auth.queries import UserQuery as AuthUserQuery
from src.modules.auth.mutations import AuthMutation
from src.modules.user.queries import UserQuery
from src.modules.user.mutations import UserMutation
from src.modules.workspace.queries import WorkspaceQuery
from src.modules.workspace.mutations import WorkspaceMutation


logger = logging.getLogger(__name__)


@strawberry.type
class Query(UserQuery, AuthUserQuery, WorkspaceQuery):
    pass


@strawberry.type
class Mutation(AuthMutation, UserMutation, WorkspaceMutation):
    pass


schema = CustomSchema(query=Query, mutation=Mutation)


schema = CustomSchema(query=Query, mutation=Mutation)

# schema = strawberry.Schema(query=Query, mutation=Mutation)