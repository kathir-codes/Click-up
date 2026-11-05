
from uuid import UUID
from datetime import datetime

from sqlalchemy.orm import Session

from src.models.task import Task, TaskStatus, TaskPriority


# -----------------------------
# CREATE TASK RECORD
# -----------------------------

def create_task_record(
    session: Session,
    workspace_id: UUID,
    title: str,
    description: str | None,
    created_by: UUID,
    status: TaskStatus = TaskStatus.TODO,
    priority: TaskPriority = TaskPriority.MEDIUM,
    assignee_id: UUID | None = None,
    due_date: datetime | None = None,
) -> Task:

    task = Task(
        workspace_id=workspace_id,
        title=title,
        description=description,
        created_by=created_by,
        status=status,
        priority=priority,
        assignee_id=assignee_id,
        due_date=due_date,
    )

    session.add(task)
    session.flush()

    return task


# -----------------------------
# GET TASKS BY WORKSPACE
# -----------------------------

def get_tasks_by_workspace(
    session: Session,
    workspace_id: UUID,
) -> list[Task]:

    return (
        session.query(Task)
        .filter(Task.workspace_id == workspace_id)
        .order_by(Task.created_at.desc())
        .all()
    )


# -----------------------------
# GET TASK BY ID
# -----------------------------

def get_task_by_id(
    session: Session,
    task_id: UUID,
    workspace_id: UUID,
) -> Task | None:

    return (
        session.query(Task)
        .filter(
            Task.task_id == task_id,
            Task.workspace_id == workspace_id,
        )
        .first()
    )


# -----------------------------
# UPDATE TASK RECORD
# -----------------------------

def update_task_record(
    session: Session,
    task: Task,
    title: str | None = None,
    description: str | None = None,
    due_date: datetime | None = None,
    status: TaskStatus | None = None,
    priority: TaskPriority | None = None,
) -> Task:

    if title is not None:
        task.title = title

    if description is not None:
        task.description = description

    if due_date is not None:
        task.due_date = due_date

    if status is not None:
        task.status = status

    if priority is not None:
        task.priority = priority

    session.flush()

    return task


# -----------------------------
# DELETE TASK RECORD
# -----------------------------

def delete_task_record(
    session: Session,
    task: Task,
) -> None:

    session.delete(task)
    session.flush()


# -----------------------------
# ASSIGN TASK RECORD
# -----------------------------

def assign_task_record(
    session: Session,
    task: Task,
    assignee_id: UUID | None,
) -> Task:

    task.assignee_id = assignee_id

    session.flush()

    return task
    