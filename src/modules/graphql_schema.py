import logging

import strawberry

from src.exceptions.graphql_error_handler import CustomSchema
from src.modules.auth.mutations import AuthMutation

# Auth
from src.modules.auth.queries import UserQuery as AuthUserQuery
from src.modules.invitation.mutations import InvitationMutation

# Invitation
from src.modules.invitation.queries import InvitationQuery
from src.modules.tag.mutations import TagMutation

# Tag
from src.modules.tag.queries import TagQuery
from src.modules.task.mutations import TaskCommentMutation, TaskMutation

# Task
from src.modules.task.queries import TaskActivityQuery, TaskCommentQuery, TaskQuery
from src.modules.user.mutations import UserMutation

# User
from src.modules.user.queries import UserQuery
from src.modules.workspace.mutations import WorkspaceMutation

# Workspace
from src.modules.workspace.queries import WorkspaceQuery

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
