from datetime import datetime
from enum import Enum

import strawberry


@strawberry.enum
class TaskStatusType(Enum):
    TODO = "TODO"
    IN_PROGRESS = "IN_PROGRESS"
    DONE = "DONE"


@strawberry.enum
class TaskPriorityType(Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    URGENT = "URGENT"


@strawberry.type
class TaskType:
    task_id: str
    workspace_id: str
    parent_task_id: str | None
    title: str
    description: str | None
    status: TaskStatusType
    priority: TaskPriorityType
    assignee_id: str | None
    created_by: str
    due_date: datetime | None
    created_at: datetime
    updated_at: datetime


@strawberry.type
class TaskCommentType:
    comment_id: str
    task_id: str
    user_id: str
    content: str
    created_at: datetime
    updated_at: datetime


@strawberry.type
class TaskActivityType:
    activity_id: str
    task_id: str
    user_id: str | None
    field: str
    old_value: str | None
    new_value: str | None
    created_at: datetime
