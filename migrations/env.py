from logging.config import fileConfig

from alembic import context

from src.core.database import engine
from src.db.base import Base

# Import all models so SQLAlchemy registers their tables.
from src.models.user import User, UserProfile
from src.models.workspace import Workspace, WorkspaceMember
from src.models.role import Role, Permission, RolePermission
from src.models.tag import Tag, TaskTag
from src.models.invitation import Invitation
from src.models.task import (
    TaskStatus,
    TaskPriority,
    TaskActivityField,
    Task,
    TaskActivity,
    TaskComment,
)

config = context.config
    
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Give Alembic access to all registered SQLAlchemy tables.
target_metadata = Base.metadata
print("Registered tables:", sorted(target_metadata.tables.keys()))

def run_migrations_offline() -> None:
    """Generate SQL without connecting directly to the database."""

    context.configure(
        url=engine.url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations using the existing database engine."""

    with engine.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online() 