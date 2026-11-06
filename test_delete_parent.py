from src.core.database import SessionLocal

# Register models
from src.models.task import Task, TaskComment, TaskActivity
from src.models.workspace import Workspace
from src.models.user import User


with SessionLocal() as session:

    # Find your test task
    task = session.query(Task).filter(
        Task.title == "DELETE TEST TASK"
    ).first()

    if not task:
        print("Test task not found")

    else:
        task_id = task.task_id

        print("Deleting task:", task.title)

        # Delete parent Task
        session.delete(task)
        session.commit()

        print("Parent task deleted!")

        # Verify database records
        comments_count = session.query(TaskComment).filter(
            TaskComment.task_id == task_id
        ).count()

        activities_count = session.query(TaskActivity).filter(
            TaskActivity.task_id == task_id
        ).count()

        print("Remaining comments:", comments_count)
        print("Remaining activities:", activities_count)