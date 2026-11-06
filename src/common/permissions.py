from enum import Enum


class Permission(str, Enum):

    # Workspace Permissions
    CREATE_WORKSPACE = "Create a workspace"
    UPDATE_WORKSPACE = "Update a workspace"
    DELETE_WORKSPACE = "Delete a workspace"

    # Member and Invitation Permissions
    INVITE_MEMBER = "Invite workspace members"
    VIEW_INVITATIONS = "View workspace invitations"
    VIEW_WORKSPACE_MEMBERS = "View workspace members"
    CANCEL_INVITATION = "Cancel an invitation"
    RESEND_INVITATION = "Resend an invitation"
    REMOVE_MEMBER = "Remove a workspace member"

    # Role and Permission Management
    VIEW_ROLES = "View workspace roles"
    CREATE_ROLE = "Create a custom role"
    UPDATE_ROLE = "Update a role"
    DELETE_ROLE = "Delete a custom role"
    MANAGE_ROLE_PERMISSIONS = "Assign permissions to roles"

    # Task Permissions
    CREATE_TASK = "Create a task"
    VIEW_TASK = "View task details"
    UPDATE_TASK = "Update a task"
    DELETE_TASK = "Delete a task"
    ASSIGN_TASK = "Assign a task"
    UPDATE_TASK_STATUS = "Update task status"
    UPDATE_TASK_PRIORITY = "Update task priority"

    # Tag Permissions
    CREATE_TAG = "Create a tag"
    UPDATE_TAG = "Update a tag"
    DELETE_TAG = "Delete a tag"
    MANAGE_TASK_TAGS = "Add or remove task tags"

    # Comment Permissions
    ADD_COMMENT = "Add a comment"
    UPDATE_COMMENT = "Update a comment"
    DELETE_COMMENT = "Delete a comment"

    # Task Activity Permissions
    VIEW_TASK_ACTIVITY = "View task activity history"