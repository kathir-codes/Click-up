from src.core.database import SessionLocal

# Import models to register their tables with SQLAlchemy
from src.models.task import Task, TaskComment, TaskActivity
from src.models.workspace import Workspace
from src.models.user import User


with SessionLocal() as session:

    task = session.query(Task).first()

    if not task:
        print("No task found")

    elif not task.comments:
        print("This task has no comments")

    else:
        comment = task.comments[0]

        print("Task:", task.title)
        print("Comment before removal:", comment.content)

        # Remove comment from parent's collection
        task.comments.remove(comment)

        # Save changes
        session.commit()

        print("Comment deleted successfully!")

        # Verify that the parent task still exists
        remaining_task = session.get(Task, task.task_id)

        print("Parent task still exists:", remaining_task is not None)