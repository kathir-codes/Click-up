from uuid import UUID

from sqlalchemy.orm import Session

from src.models.task import TaskActivity, TaskActivityField

# -----------------------------
# CREATE TASK ACTIVITY
# -----------------------------


def create_task_activity(
    session: Session,
    task_id: UUID,
    user_id: UUID,
    field: TaskActivityField,
    old_value: str | None,
    new_value: str | None,
) -> TaskActivity:

    activity = TaskActivity(
        task_id=task_id,
        user_id=user_id,
        field=field,
        old_value=old_value,
        new_value=new_value,
    )

    session.add(activity)
    session.flush()

    return activity


# -----------------------------
# GET TASK ACTIVITIES
# -----------------------------


def get_task_activities(
    session: Session,
    task_id: UUID,
) -> list[TaskActivity]:

    return (
        session.query(TaskActivity)
        .filter(TaskActivity.task_id == task_id)
        .order_by(TaskActivity.created_at.desc())
        .all()
    )
