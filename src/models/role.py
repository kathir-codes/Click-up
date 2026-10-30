
from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import (
    Boolean,
    DateTime,
    ForeignKey,
    String,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column
from src.database.base import Base


class Role(Base):
    __tablename__ = "roles"

    __table_args__ = (
        UniqueConstraint(
            "workspace_id",
            "role_name",
            name="uq_workspace_role_name",
        ),
        UniqueConstraint(
            "workspace_id",
            "role_id",
            name="uq_workspace_role_id",
        ),
    )

    role_id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
    )

    workspace_id: Mapped[UUID] = mapped_column(
        ForeignKey("workspaces.workspace_id", ondelete="CASCADE"),
        nullable=False,
    )

    role_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    is_system_role: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
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

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )


class Permission(Base):
    __tablename__ = "permissions"

    permission_id: Mapped[UUID] = mapped_column(
        primary_key=True,
        default=uuid4,
    )

    permission_name: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
    )

    description: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )


class RolePermission(Base):
    __tablename__ = "role_permissions"

    role_id: Mapped[UUID] = mapped_column(
        ForeignKey("roles.role_id", ondelete="CASCADE"),
        primary_key=True,
    )

    permission_id: Mapped[UUID] = mapped_column(
        ForeignKey("permissions.permission_id", ondelete="CASCADE"),
        primary_key=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
