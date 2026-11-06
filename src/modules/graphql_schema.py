import logging
import strawberry

from src.exceptions.graphql_error_handler import CustomSchema

# Auth
from src.modules.auth.queries import UserQuery as AuthUserQuery
from src.modules.auth.mutations import AuthMutation

# User
from src.modules.user.queries import UserQuery
from src.modules.user.mutations import UserMutation

# Workspace
from src.modules.workspace.queries import WorkspaceQuery
from src.modules.workspace.mutations import WorkspaceMutation

# Invitation
from src.modules.invitation.queries import InvitationQuery
from src.modules.invitation.mutations import InvitationMutation

# Task
from src.modules.task.queries import (
    TaskQuery,
    TaskCommentQuery,
    TaskActivityQuery,
)
from src.modules.task.mutations import (
    TaskMutation,
    TaskCommentMutation,
)

# Tag
from src.modules.tag.queries import TagQuery
from src.modules.tag.mutations import TagMutation


logger = logging.getLogger(__name__)


@strawberry.type
class Query(
    UserQuery,
    AuthUserQuery,
    WorkspaceQuery,
    InvitationQuery,
    TaskQuery,
    TaskCommentQuery,
    TaskActivityQuery,
    TagQuery,
):
    pass


@strawberry.type
class Mutation(
    AuthMutation,
    UserMutation,
    WorkspaceMutation,
    InvitationMutation,
    TaskMutation,
    TaskCommentMutation,
    TagMutation,
):
    pass


schema = CustomSchema(
    query=Query,
    mutation=Mutation,
)