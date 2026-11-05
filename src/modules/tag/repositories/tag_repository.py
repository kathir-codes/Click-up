from uuid import UUID

from sqlalchemy.orm import Session

from src.models.tag import Tag, TaskTag


# CREATE TAG

def create_tag_record(
    session: Session,
    workspace_id: UUID,
    name: str,
    user_id: UUID,
) -> Tag:

    tag = Tag(
        workspace_id=workspace_id,
        name=name,
        created_by=user_id,
    )

    session.add(tag)
    session.flush()

    return tag


# GET TAG BY NAME

def get_tag_by_name(
    session: Session,
    workspace_id: UUID,
    name: str,
) -> Tag | None:

    return (
        session.query(Tag)
        .filter(
            Tag.workspace_id == workspace_id,
            Tag.name == name,
        )
        .first()
    )


# GET TAG BY ID

def get_tag_by_id(
    session: Session,
    tag_id: UUID,
    workspace_id: UUID,
) -> Tag | None:

    return (
        session.query(Tag)
        .filter(
            Tag.tag_id == tag_id,
            Tag.workspace_id == workspace_id,
        )
        .first()
    )


# GET ALL WORKSPACE TAGS

def get_tags_by_workspace(
    session: Session,
    workspace_id: UUID,
) -> list[Tag]:

    return (
        session.query(Tag)
        .filter(Tag.workspace_id == workspace_id)
        .order_by(Tag.created_at.asc())
        .all()
    )


# GET TASK TAG ASSIGNMENT

def get_task_tag(
    session: Session,
    task_id: UUID,
    tag_id: UUID,
    workspace_id: UUID,
) -> TaskTag | None:

    return (
        session.query(TaskTag)
        .filter(
            TaskTag.task_id == task_id,
            TaskTag.tag_id == tag_id,
            TaskTag.workspace_id == workspace_id,
        )
        .first()
    )


# ASSIGN TAG TO TASK

def assign_tag_record(
    session: Session,
    task_id: UUID,
    tag_id: UUID,
    workspace_id: UUID,
    user_id: UUID,
) -> TaskTag:

    task_tag = TaskTag(
        task_id=task_id,
        tag_id=tag_id,
        workspace_id=workspace_id,
        added_by=user_id,
    )

    session.add(task_tag)
    session.flush()

    return task_tag


# REMOVE TAG FROM TASK

def remove_tag_record(
    session: Session,
    task_tag: TaskTag,
) -> None:

    session.delete(task_tag)
    session.flush()