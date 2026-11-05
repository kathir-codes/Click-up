
from uuid import UUID

from sqlalchemy.orm import Session

from src.common.permissions import Permission
from src.models.task import TaskActivityField

from src.modules.authorization.service import (
    check_workspace_permission,
)

from src.modules.task.repositories import task_repository
from src.modules.task.services.activity_service import create_task_activity

from src.modules.tag.repositories import tag_repository


# -----------------------------
# CREATE TAG
# -----------------------------

def create_tag(
    session: Session,
    workspace_id: UUID,
    name: str,
    user_id: UUID,
):

    try:
        has_permission = check_workspace_permission(
            session=session,
            workspace_id=workspace_id,
            user_id=user_id,
            permission_name=Permission.CREATE_TAG,
        )

        if not has_permission:
            raise ValueError(
                "You do not have permission to create tags."
            )

        name = name.strip()

        if not name:
            raise ValueError("Tag name cannot be empty.")

        if len(name) > 100:
            raise ValueError(
                "Tag name cannot exceed 100 characters."
            )

        existing_tag = tag_repository.get_tag_by_name(
            session=session,
            workspace_id=workspace_id,
            name=name,
        )

        if existing_tag:
            raise ValueError(
                "A tag with this name already exists in this workspace."
            )

        tag = tag_repository.create_tag_record(
            session=session,
            workspace_id=workspace_id,
            name=name,
            user_id=user_id,
        )

        session.commit()
        session.refresh(tag)

        return tag

    except Exception:
        session.rollback()
        raise


# -----------------------------
# GET ALL WORKSPACE TAGS
# -----------------------------

def get_workspace_tags(
    session: Session,
    workspace_id: UUID,
    user_id: UUID,
):

    has_permission = check_workspace_permission(
        session=session,
        workspace_id=workspace_id,
        user_id=user_id,
        permission_name=Permission.VIEW_TASK,
    )

    if not has_permission:
        raise ValueError(
            "You do not have permission to view workspace tags."
        )

    return tag_repository.get_tags_by_workspace(
        session=session,
        workspace_id=workspace_id,
    )


# -----------------------------
# ASSIGN TAG TO TASK
# -----------------------------

def assign_tag_to_task(
    session: Session,
    task_id: UUID,
    tag_id: UUID,
    workspace_id: UUID,
    user_id: UUID,
):

    try:
        has_permission = check_workspace_permission(
            session=session,
            workspace_id=workspace_id,
            user_id=user_id,
            permission_name=Permission.MANAGE_TASK_TAGS,
        )

        if not has_permission:
            raise ValueError(
                "You do not have permission to manage task tags."
            )

        # Check task belongs to workspace
        task = task_repository.get_task_by_id(
            session=session,
            task_id=task_id,
            workspace_id=workspace_id,
        )

        if task is None:
            raise ValueError("Task not found.")

        # Check tag belongs to workspace
        tag = tag_repository.get_tag_by_id(
            session=session,
            tag_id=tag_id,
            workspace_id=workspace_id,
        )

        if tag is None:
            raise ValueError(
                "Tag not found in this workspace."
            )

        # Check duplicate assignment
        existing_assignment = tag_repository.get_task_tag(
            session=session,
            task_id=task_id,
            tag_id=tag_id,
            workspace_id=workspace_id,
        )

        if existing_assignment:
            raise ValueError(
                "Tag is already assigned to this task."
            )

        tag_repository.assign_tag_record(
            session=session,
            task_id=task_id,
            tag_id=tag_id,
            workspace_id=workspace_id,
            user_id=user_id,
        )

        create_task_activity(
            session=session,
            task_id=task_id,
            user_id=user_id,
            field=TaskActivityField.TAG_ADDED,
            old_value=None,
            new_value=tag.name,
        )

        session.commit()
        session.refresh(tag)

        return tag

    except Exception:
        session.rollback()
        raise


# -----------------------------
# REMOVE TAG FROM TASK
# -----------------------------

def remove_tag_from_task(
    session: Session,
    task_id: UUID,
    tag_id: UUID,
    workspace_id: UUID,
    user_id: UUID,
) -> bool:

    try:
        has_permission = check_workspace_permission(
            session=session,
            workspace_id=workspace_id,
            user_id=user_id,
            permission_name=Permission.MANAGE_TASK_TAGS,
        )

        if not has_permission:
            raise ValueError(
                "You do not have permission to manage task tags."
            )

        # Check task belongs to workspace
        task = task_repository.get_task_by_id(
            session=session,
            task_id=task_id,
            workspace_id=workspace_id,
        )

        if task is None:
            raise ValueError("Task not found.")

        # Check tag assignment
        task_tag = tag_repository.get_task_tag(
            session=session,
            task_id=task_id,
            tag_id=tag_id,
            workspace_id=workspace_id,
        )

        if task_tag is None:
            raise ValueError(
                "This tag is not assigned to the task."
            )

        # Get tag details before removing assignment
        tag = tag_repository.get_tag_by_id(
            session=session,
            tag_id=tag_id,
            workspace_id=workspace_id,
        )

        if tag is None:
            raise ValueError(
                "Tag not found in this workspace."
            )

        tag_repository.remove_tag_record(
            session=session,
            task_tag=task_tag,
        )

        create_task_activity(
            session=session,
            task_id=task_id,
            user_id=user_id,
            field=TaskActivityField.TAG_REMOVED,
            old_value=tag.name,
            new_value=None,
        )

        session.commit()

        return True

    except Exception:
        session.rollback()
        raise
