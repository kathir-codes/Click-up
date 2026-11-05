
from src.core.database import SessionLocal
from src.common.permissions import Permission
from src.models.role import Permission as PermissionModel


def seed_permissions():
    with SessionLocal() as session:
        try:
            # Get existing permission names from the database.
            existing_permissions = {
                name
                for (name,) in session.query(
                    PermissionModel.permission_name
                ).all()
            }

            # Insert only missing permissions from the Enum.
            for permission in Permission:
                if permission.value not in existing_permissions:
                    session.add(
                        PermissionModel(
                            permission_name=permission.value,
                            description=permission.name.replace(
                                "_", " "
                            ).title(),
                        )
                    )

            session.commit()

            print("Permission seeding completed successfully.")

        except Exception:
            session.rollback()
            raise


if __name__ == "__main__":
    seed_permissions()
