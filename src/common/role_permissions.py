from src.common.permissions import Permission

# ==================== Owner Role Permissions ====================
# Owner receives all permissions except CREATE_WORKSPACE.

ROLE_PERMISSIONS = {
    "Owner": set(Permission),
    # ==================== Admin Role Permissions ====================
    "Admin": {
        Permission.UPDATE_WORKSPACE,
        Permission.VIEW_INVITATIONS,
        Permission.CANCEL_INVITATION,
        Permission.VIEW_WORKSPACE_MEMBERS,
        Permission.INVITE_MEMBER,
        Permission.RESEND_INVITATION,
        Permission.REMOVE_MEMBER,
        Permission.VIEW_ROLES,
        Permission.CREATE_TASK,
        Permission.VIEW_TASK,
        Permission.UPDATE_TASK,
        Permission.DELETE_TASK,
        Permission.ASSIGN_TASK,
        Permission.UPDATE_TASK_STATUS,
        Permission.UPDATE_TASK_PRIORITY,
        Permission.CREATE_TAG,
        Permission.UPDATE_TAG,
        Permission.MANAGE_TASK_TAGS,
        Permission.ADD_COMMENT,
        Permission.UPDATE_COMMENT,
        Permission.DELETE_COMMENT,
        Permission.VIEW_TASK_ACTIVITY,
    },
    # ==================== Member Role Permissions ====================
    "Member": {
        Permission.CREATE_TASK,
        Permission.VIEW_TASK,
        Permission.UPDATE_TASK,
        Permission.UPDATE_TASK_STATUS,
        Permission.ADD_COMMENT,
        Permission.VIEW_TASK_ACTIVITY,
    },
}
