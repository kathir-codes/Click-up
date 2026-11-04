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
from src.modules.invitation.mutations import InvitationMutation
from src.modules.invitation.queries import InvitationQuery

logger = logging.getLogger(__name__)


@strawberry.type
class Query(UserQuery, AuthUserQuery, WorkspaceQuery, InvitationQuery):
    pass


@strawberry.type
class Mutation(AuthMutation, UserMutation, WorkspaceMutation, InvitationMutation):
    pass


schema = CustomSchema(query=Query, mutation=Mutation)

# schema = strawberry.Schema(query=Query, mutation=Mutation)
