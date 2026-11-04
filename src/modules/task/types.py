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
