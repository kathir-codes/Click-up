from uuid import UUID

from sqlalchemy.orm import Session

from src.models.workspace import Workspace
from src.modules.workspace import repository


def create_workspace(
    session: Session,
    name: str,
    slug: str,
    description: str | None,
    creator_user_id: UUID,
) -> Workspace:
    return repository.create_workspace(
        session=session,
        name=name,
        slug=slug,
        description=description,
        creator_user_id=creator_user_id,
    )


def update_workspace(
    session: Session,
    workspace_id: UUID,
    name: str | None = None,
    slug: str | None = None,
    description: str | None = None,
) -> Workspace | None:
    return repository.update_workspace(
        session=session,
        workspace_id=workspace_id,
        name=name,
        slug=slug,
        description=description,
    )


def delete_workspace(
    session: Session,
    workspace_id: UUID,
) -> bool:
    return repository.delete_workspace(
        session=session,
        workspace_id=workspace_id,
    )


def get_user_workspaces(
    session: Session,
    user_id: UUID,
) -> list[Workspace]:
    return repository.get_user_workspaces(
        session=session,
        user_id=user_id,
    )


def get_user_workspace(
    session: Session,
    workspace_id: UUID,
    user_id: UUID,
) -> Workspace | None:
    return repository.get_user_workspace(
        session=session,
        workspace_id=workspace_id,
        user_id=user_id,
    )