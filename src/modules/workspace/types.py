import strawberry


@strawberry.type
class WorkspaceType:
    workspace_id: str
    name: str
    slug: str
    description: str | None