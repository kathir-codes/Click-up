from src.models.task import Task


def get_tasks_by_workspace(session, workspace_id):
    return (
        session.query(Task)
        .filter(Task.workspace_id == workspace_id)
        .order_by(Task.created_at.desc())
        .all()
    )