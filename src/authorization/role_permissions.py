
from src.authorization.permissions import PERMISSIONS


# ==================== Owner Role Permissions ====================
# Owner receives all workspace permissions except CREATE_WORKSPACE.
ROLE_PERMISSIONS = {
    "Owner": set(PERMISSIONS),

    # ==================== Admin Role Permissions ====================
    "Admin": {
        "UPDATE_WORKSPACE",
        "INVITE_MEMBER",
        "RESEND_INVITATION",
        "REMOVE_MEMBER",
        "VIEW_ROLES",
        "CREATE_TASK",
        "VIEW_TASK",
        "UPDATE_TASK",
        "DELETE_TASK",
        "ASSIGN_TASK",
        "UPDATE_TASK_STATUS",
        "UPDATE_TASK_PRIORITY",
        "CREATE_TAG",
        "UPDATE_TAG",
        "MANAGE_TASK_TAGS",
        "ADD_COMMENT",
        "UPDATE_COMMENT",
        "DELETE_COMMENT",
        "VIEW_TASK_ACTIVITY",
    },

    # ==================== Member Role Permissions ====================
    "Member": {
        "CREATE_TASK",
        "VIEW_TASK",
        "UPDATE_TASK",
        "UPDATE_TASK_STATUS",
        "ADD_COMMENT",
        "VIEW_TASK_ACTIVITY",
    },
}
