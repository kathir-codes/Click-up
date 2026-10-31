from src.core.database import SessionLocal
from src.common.permissions import PERMISSIONS
from src.models.role import Permission


def seed_permissions():
    with SessionLocal() as session:
        try:
            # Get permission names that already exist in the database.
            existing_permissions = {
                name
                for (name,) in session.query(Permission.permission_name).all()
            }

            # Insert only permissions that are missing.
            for permission_name, description in PERMISSIONS.items():
                if permission_name not in existing_permissions:
                    permission = Permission(
                        permission_name=permission_name,
                        description=description,
                    )
                    session.add(permission)

            # Save all new permissions to the database.
            session.commit()

            print("Permission seeding completed successfully.")

        except Exception:
            session.rollback()
            raise




if __name__ == "__main__":
    seed_permissions()