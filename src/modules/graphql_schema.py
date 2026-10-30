import strawberry

from src.modules.auth.queries import UserQuery
from src.modules.auth.mutations import AuthMutation
from src.modules.workspace.queries import WorkspaceQuery
from src.modules.workspace.mutations import WorkspaceMutation

@strawberry.type
class Query(UserQuery,  WorkspaceQuery):
    pass


@strawberry.type
class Mutation(AuthMutation, WorkspaceMutation):
    pass


schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
)