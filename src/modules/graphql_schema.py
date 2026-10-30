import strawberry

from src.modules.auth.queries import UserQuery
from src.modules.auth.mutations import AuthMutation


@strawberry.type
class Query(UserQuery):
    pass


@strawberry.type
class Mutation(AuthMutation):
    pass


schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
)