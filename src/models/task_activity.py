import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, text
from sqlalchemy.dialects.postgresql import UUID, ENUM
from sqlalchemy.orm import Mapped, mapped_column

from src.database.base import Base


class TaskActivity(Base):
    __tablename__ = "task_activity"

    activity_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    task_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tasks.task_id", ondelete="CASCADE"),
        nullable=False,
    )

    user_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.user_id", ondelete="SET NULL"),
        nullable=True,
    )

    field: Mapped[str] = mapped_column(
        ENUM(
            "STATUS",
            "PRIORITY",
            name="task_activity_field",
            schema="public",
            create_type=False,
        ),
        nullable=False,
    )

    old_value: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    new_value: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=text("now()"),
    )