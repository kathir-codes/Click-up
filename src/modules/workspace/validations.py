
import re
from uuid import UUID

from pydantic import BaseModel, Field, field_validator


class CreateWorkspacePayload(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    slug: str = Field(min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=500)

    @field_validator("name")
    @classmethod
    def validate_name(cls, value):
        value = value.strip()

        if not value:
            raise ValueError(
                "Workspace name cannot be empty or spaces."
            )

        return value

    @field_validator("slug")
    @classmethod
    def validate_slug(cls, value):
        value = value.lower()

        if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", value):
            raise ValueError("Invalid workspace slug.")

        return value


class UpdateWorkspacePayload(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    slug: str | None = Field(default=None, min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=500)

    @field_validator("name")
    @classmethod
    def validate_name(cls, value):
        if value is not None:
            value = value.strip()

            if not value:
                raise ValueError(
                    "Workspace name cannot be empty or spaces."
                )

        return value

    @field_validator("slug")
    @classmethod
    def validate_slug(cls, value):
        if value is not None:
            value = value.lower()

            if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", value):
                raise ValueError("Invalid workspace slug.")

        return value


class WorkspaceIDPayload(BaseModel):
    workspace_id: UUID


class RemoveWorkspaceMemberPayload(BaseModel):
    workspace_id: UUID
    target_user_id: UUID
