from datetime import datetime
import strawberry


@strawberry.type
class TagType:
    tag_id: str
    workspace_id: str
    name: str
    created_by: str
    created_at: datetime