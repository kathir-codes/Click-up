from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import (
    DateTime,
    ForeignKey,
    ForeignKeyConstraint,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from src.database.base import Base


class Tag(Base):
    __tablename__ = "tags"

    __table_args__ = (
        UniqueConstraint(
            "workspace_id",
            "name",
            name="uq_workspace_tag_name",
        ),
        UniqueConstraint(
            "workspace_id",
            "tag_id",
            name="uq_workspace_tag_id",
        ),
    )

    tag_id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
    )

    workspace_id: Mapped[UUID] = mapped_column(
        ForeignKey("workspaces.workspace_id", ondelete="CASCADE"),
        nullable=False,
    )

    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    created_by: Mapped[UUID] = mapped_column(
        ForeignKey("users.user_id"),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )


class TaskTag(Base):
    __tablename__ = "task_tags"

    __table_args__ = (
        ForeignKeyConstraint(
            ["workspace_id", "task_id"],
            ["tasks.workspace_id", "tasks.task_id"],
            name="fk_task_tag_same_workspace_task",
            ondelete="CASCADE",
        ),
        ForeignKeyConstraint(
            ["workspace_id", "tag_id"],
            ["tags.workspace_id", "tags.tag_id"],
            name="fk_task_tag_same_workspace_tag",
            ondelete="CASCADE",
        ),
    )

    workspace_id: Mapped[UUID] = mapped_column(
        primary_key=True,
    )

    task_id: Mapped[UUID] = mapped_column(
        primary_key=True,
    )

    tag_id: Mapped[UUID] = mapped_column(
        primary_key=True,
    )

    added_by: Mapped[UUID] = mapped_column(
        ForeignKey("users.user_id"),
        nullable=False,
    )

    added_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )