import strawberry

from src.modules.auth.queries import UserQuery as AuthUserQuery
from src.modules.auth.mutations import AuthMutation
from src.modules.user.queries import UserQuery
from src.modules.user.mutations import UserMutation
from src.modules.workspace.queries import WorkspaceQuery
from src.modules.workspace.mutations import WorkspaceMutation


@strawberry.type
class Query(UserQuery, AuthUserQuery, WorkspaceQuery):
    pass


@strawberry.type
class Mutation(AuthMutation, UserMutation, WorkspaceMutation):
    pass


schema = strawberry.Schema(query=Query, mutation=Mutation)