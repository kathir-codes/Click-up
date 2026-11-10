
from uuid import UUID

from sqlalchemy.orm import Session

from src.common.permissions import Permission
from src.models.task import TaskActivityField, TaskComment
from src.modules.authorization.decorators import require_workspace_permission
from src.modules.task.repositories import comment_repository, task_repository
from src.modules.task.services.activity_service import create_task_activity

# -----------------------------
# CREATE COMMENT
# -----------------------------

@require_workspace_permission(Permission.ADD_COMMENT)
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

        task = task_repository.get_task_by_id(
            session=session,
            task_id=task_id,
            workspace_id=workspace_id,
        )

        if task is None:
            raise ValueError("Task not found.") 
        
        if task.deleted_at is not None:
            raise ValueError("Cannot add a comment to a deleted task.")

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

@require_workspace_permission(Permission.VIEW_TASK)
def get_task_comments(
    session: Session,
    task_id: UUID,
    workspace_id: UUID,
    user_id: UUID,
) -> list[TaskComment]:

    task = task_repository.get_task_by_id(
        session=session,
        task_id=task_id,
        workspace_id=workspace_id,
    )

    if task is None:
        raise ValueError("Task not found.")

    if task.deleted_at is not None:
        raise ValueError("Cannot view comments of a deleted task.")

    return comment_repository.get_comments_by_task(
        session=session,
        task_id=task_id,
    )


# -----------------------------
# UPDATE OWN COMMENT
# -----------------------------

@require_workspace_permission(Permission.UPDATE_COMMENT)
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

        task = task_repository.get_task_by_id(
            session=session,
            task_id=task_id,
            workspace_id=workspace_id,
        )

        if task is None:
            raise ValueError("Task not found.")

        if task.deleted_at is not None:
            raise ValueError("Cannot update a comment on a deleted task.")

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

@require_workspace_permission(Permission.DELETE_COMMENT)
def delete_task_comment(
    session: Session,
    comment_id: UUID,
    task_id: UUID,
    workspace_id: UUID,
    user_id: UUID,
) -> bool:

    try:
        task = task_repository.get_task_by_id(
            session=session,
            task_id=task_id,
            workspace_id=workspace_id,
        )

        if task is None:
            raise ValueError("Task not found.")

        if task.deleted_at is not None:
            raise ValueError("Cannot delete a comment from a deleted task.")

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
