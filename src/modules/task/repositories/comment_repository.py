
from uuid import UUID

from sqlalchemy.orm import Session

from src.models.task import TaskComment


# -----------------------------
# CREATE COMMENT RECORD
# -----------------------------

def create_comment_record(
    session: Session,
    task_id: UUID,
    user_id: UUID,
    content: str,
) -> TaskComment:

    comment = TaskComment(
        task_id=task_id,
        user_id=user_id,
        content=content,
    )

    session.add(comment)
    session.flush()

    return comment


# -----------------------------
# GET COMMENTS BY TASK
# -----------------------------

def get_comments_by_task(
    session: Session,
    task_id: UUID,
) -> list[TaskComment]:

    return (
        session.query(TaskComment)
        .filter(TaskComment.task_id == task_id)
        .order_by(TaskComment.created_at.asc())
        .all()
    )


# -----------------------------
# GET COMMENT BY ID
# -----------------------------

def get_comment_by_id(
    session: Session,
    comment_id: UUID,
    task_id: UUID,
) -> TaskComment | None:

    return (
        session.query(TaskComment)
        .filter(
            TaskComment.comment_id == comment_id,
            TaskComment.task_id == task_id,
        )
        .first()
    )


# -----------------------------
# UPDATE COMMENT RECORD
# -----------------------------

def update_comment_record(
    session: Session,
    comment: TaskComment,
    content: str,
) -> TaskComment:

    comment.content = content

    session.flush()

    return comment


# -----------------------------
# DELETE COMMENT RECORD
# -----------------------------

def delete_comment_record(
    session: Session,
    comment: TaskComment,
) -> None:

    session.delete(comment)
    session.flush()
