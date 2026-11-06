
from uuid import UUID

from sqlalchemy.orm import Session

from src.common.permissions import Permission
from src.models.task import TaskComment, TaskActivityField

from src.modules.task.repositories import (
    task_repository,
    comment_repository,
)

from src.modules.task.services.activity_service import create_task_activity
from src.modules.authorization.service import check_workspace_permission


# -----------------------------
# CREATE COMMENT
# -----------------------------

def create_task_comment(
    session: Session,
    task_id: UUID,
    workspace_id: UUID,
    user_id: UUID,
    content: str,
) -> TaskComment:

    try:
        content = content.strip()

        if not content:
            raise ValueError("Comment cannot be empty.")

        has_permission = check_workspace_permission(
            session=session,
            workspace_id=workspace_id,
            user_id=user_id,
            permission_name=Permission.ADD_COMMENT,
        )

        if not has_permission:
            raise ValueError(
                "You do not have permission to comment on this task."
            )

        task = task_repository.get_task_by_id(
            session=session,
            task_id=task_id,
            workspace_id=workspace_id,
        )

        if task is None:
            raise ValueError("Task not found.")

        comment = comment_repository.create_comment_record(
            session=session,
            task_id=task_id,
            user_id=user_id,
            content=content,
        )

        create_task_activity(
            session=session,
            task_id=task_id,
            user_id=user_id,
            field=TaskActivityField.COMMENT_ADDED,
            old_value=None,
            new_value=content,
        )

        session.commit()
        session.refresh(comment)

        return comment

    except Exception:
        session.rollback()
        raise


# -----------------------------
# GET TASK COMMENTS
# -----------------------------

def get_task_comments(
    session: Session,
    task_id: UUID,
    workspace_id: UUID,
    user_id: UUID,
) -> list[TaskComment]:

    has_permission = check_workspace_permission(
        session=session,
        workspace_id=workspace_id,
        user_id=user_id,
        permission_name=Permission.VIEW_TASK,
    )

    if not has_permission:
        raise ValueError(
            "You do not have permission to view task comments."
        )

    task = task_repository.get_task_by_id(
        session=session,
        task_id=task_id,
        workspace_id=workspace_id,
    )

    if task is None:
        raise ValueError("Task not found.")

    return comment_repository.get_comments_by_task(
        session=session,
        task_id=task_id,
    )


# -----------------------------
# UPDATE OWN COMMENT
# -----------------------------

def update_task_comment(
    session: Session,
    comment_id: UUID,
    task_id: UUID,
    workspace_id: UUID,
    user_id: UUID,
    content: str,
) -> TaskComment:

    try:
        content = content.strip()

        if not content:
            raise ValueError("Comment cannot be empty.")

        has_permission = check_workspace_permission(
            session=session,
            workspace_id=workspace_id,
            user_id=user_id,
            permission_name=Permission.UPDATE_COMMENT,
        )

        if not has_permission:
            raise ValueError(
                "You do not have permission to update comments."
            )

        task = task_repository.get_task_by_id(
            session=session,
            task_id=task_id,
            workspace_id=workspace_id,
        )

        if task is None:
            raise ValueError("Task not found.")

        comment = comment_repository.get_comment_by_id(
            session=session,
            comment_id=comment_id,
            task_id=task_id,
        )

        if comment is None:
            raise ValueError("Comment not found.")

        if comment.user_id != user_id:
            raise ValueError("You can only update your own comments.")

        comment = comment_repository.update_comment_record(
            session=session,
            comment=comment,
            content=content,
        )

        session.commit()
        session.refresh(comment)

        return comment

    except Exception:
        session.rollback()
        raise


# -----------------------------
# DELETE OWN COMMENT
# -----------------------------

def delete_task_comment(
    session: Session,
    comment_id: UUID,
    task_id: UUID,
    workspace_id: UUID,
    user_id: UUID,
) -> bool:

    try:
        has_permission = check_workspace_permission(
            session=session,
            workspace_id=workspace_id,
            user_id=user_id,
            permission_name=Permission.DELETE_COMMENT,
        )

        if not has_permission:
            raise ValueError(
                "You do not have permission to delete comments."
            )

        task = task_repository.get_task_by_id(
            session=session,
            task_id=task_id,
            workspace_id=workspace_id,
        )

        if task is None:
            raise ValueError("Task not found.")

        comment = comment_repository.get_comment_by_id(
            session=session,
            comment_id=comment_id,
            task_id=task_id,
        )

        if comment is None:
            raise ValueError("Comment not found.")

        if comment.user_id != user_id:
            raise ValueError("You can only delete your own comments.")

        comment_repository.delete_comment_record(
            session=session,
            comment=comment,
        )

        session.commit()

        return True

    except Exception:
        session.rollback()
        raise
