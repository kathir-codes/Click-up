from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.orm import Session

from src.models.task import Task, TaskPriority, TaskStatus

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
        .filter(
            Task.workspace_id == workspace_id,
            Task.deleted_at.is_(None),
        )
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
            Task.deleted_at.is_(None),
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
# SOFT DELETE TASK RECORD
# -----------------------------


def delete_task_record(
    session: Session,
    task: Task,
) -> None:

    deleted_time = datetime.now(timezone.utc)

    # Soft delete the main task
    task.deleted_at = deleted_time

    # Soft delete active subtasks
    for subtask in task.subtasks:
        if subtask.deleted_at is None:
            subtask.deleted_at = deleted_time

    session.flush()


# -----------------------------
# GET DELETED TASKS
# -----------------------------


def get_deleted_tasks_by_workspace(
    session: Session,
    workspace_id: UUID,
) -> list[Task]:

    return (
        session.query(Task)
        .filter(
            Task.workspace_id == workspace_id,
            Task.parent_task_id.is_(None),
            Task.deleted_at.isnot(None),
        )
        .order_by(Task.deleted_at.desc())
        .all()
    )


# -----------------------------
# RESTORE TASK
# -----------------------------


def restore_task_record(
    session: Session,
    task: Task,
) -> Task:

    task.deleted_at = None

    # Restore deleted subtasks
    for subtask in task.subtasks:
        if subtask.deleted_at is not None:
            subtask.deleted_at = None

    session.flush()

    return task


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


# -----------------------------
# CREATE SUBTASK RECORD
# -----------------------------


def create_subtask_record(
    session: Session,
    parent_task: Task,
    title: str,
    description: str | None,
    created_by: UUID,
    status: TaskStatus = TaskStatus.TODO,
    priority: TaskPriority = TaskPriority.MEDIUM,
    assignee_id: UUID | None = None,
    due_date: datetime | None = None,
) -> Task:

    subtask = Task(
        workspace_id=parent_task.workspace_id,
        parent_task_id=parent_task.task_id,
        title=title,
        description=description,
        created_by=created_by,
        status=status,
        priority=priority,
        assignee_id=assignee_id,
        due_date=due_date,
    )

    session.add(subtask)
    session.flush()

    return subtask


# -----------------------------
# GET SUBTASKS BY PARENT
# -----------------------------


def get_subtasks_by_parent(
    session: Session,
    parent_task_id: UUID,
    workspace_id: UUID,
) -> list[Task]:

    return (
        session.query(Task)
        .filter(
            Task.parent_task_id == parent_task_id,
            Task.workspace_id == workspace_id,
            Task.deleted_at.is_(None),
        )
        .order_by(Task.created_at.asc())
        .all()
    )
