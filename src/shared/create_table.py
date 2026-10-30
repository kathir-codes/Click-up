from src.database.base import Base
from src.core.database import engine

# Import all models to register their tables.
from src.models.user import User, UserProfile
from src.models.workspace import Workspace, WorkspaceMember
from src.models.role import Role, Permission, RolePermission
from src.models.task import Task, TaskActivity, TaskComment 

# Uncomment this if Tag and TaskTag are defined in src/models/tag.py.
# from src.models.tag import Tag, TaskTag


def create_tables():
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    create_tables()
    print("Database tables created successfully.")