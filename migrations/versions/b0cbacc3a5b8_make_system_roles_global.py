
"""make system roles global

Revision ID: b0cbacc3a5b8
Revises: 2f71f07cc37d
Create Date: 2026-11-12 14:56:05.401376
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "b0cbacc3a5b8"
down_revision: Union[str, Sequence[str], None] = "2f71f07cc37d"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Convert workspace-specific system roles into global roles."""

    # Validate existing role data before making changes.
    op.execute("""
        DO $$
        BEGIN
            IF (
                SELECT COUNT(DISTINCT role_name)
                FROM roles
            ) <> 3 THEN
                RAISE EXCEPTION
                    'Expected exactly 3 role names: Owner, Admin, Member';
            END IF;

            IF EXISTS (
                SELECT 1
                FROM roles
                WHERE role_name NOT IN ('Owner', 'Admin', 'Member')
                   OR is_system_role IS NOT TRUE
            ) THEN
                RAISE EXCEPTION
                    'Unexpected role name or non-system role found';
            END IF;
        END $$;
    """)

    # Remove old composite foreign keys.
    op.drop_constraint(
        op.f("fk_invitation_workspace_role"),
        "invitations",
        type_="foreignkey",
    )

    op.drop_constraint(
        op.f("fk_workspace_member_role"),
        "workspace_members",
        type_="foreignkey",
    )

    # Add simple role foreign keys.
    op.create_foreign_key(
        "fk_invitation_role",
        "invitations",
        "roles",
        ["role_id"],
        ["role_id"],
    )

    op.create_foreign_key(
        "fk_workspace_member_role_id",
        "workspace_members",
        "roles",
        ["role_id"],
        ["role_id"],
    )

    # Allow global roles without a workspace or creator.
    op.alter_column(
        "roles",
        "workspace_id",
        existing_type=sa.UUID(),
        nullable=True,
    )

    op.alter_column(
        "roles",
        "created_by",
        existing_type=sa.UUID(),
        nullable=True,
    )

    # Remove workspace-specific uniqueness.
    op.drop_constraint(
        op.f("uq_workspace_role_id"),
        "roles",
        type_="unique",
    )

    op.drop_constraint(
        op.f("uq_workspace_role_name"),
        "roles",
        type_="unique",
    )

    # Create a mapping from every existing role to one canonical role.
    op.execute("""
        CREATE TEMP TABLE role_id_map ON COMMIT DROP AS
        SELECT
            role_id AS old_role_id,
            FIRST_VALUE(role_id) OVER (
                PARTITION BY role_name
                ORDER BY role_id::text
            ) AS canonical_role_id
        FROM roles;
    """)

    # Copy all existing permissions to canonical roles.
    op.execute("""
        INSERT INTO role_permissions (
            role_id,
            permission_id,
            created_at
        )
        SELECT DISTINCT
            m.canonical_role_id,
            rp.permission_id,
            NOW()
        FROM role_permissions rp
        JOIN role_id_map m
            ON rp.role_id = m.old_role_id
        ON CONFLICT (role_id, permission_id) DO NOTHING;
    """)

    # Update workspace memberships.
    op.execute("""
        UPDATE workspace_members wm
        SET role_id = m.canonical_role_id
        FROM role_id_map m
        WHERE wm.role_id = m.old_role_id
          AND m.old_role_id <> m.canonical_role_id;
    """)

    # Update invitations.
    op.execute("""
        UPDATE invitations i
        SET role_id = m.canonical_role_id
        FROM role_id_map m
        WHERE i.role_id = m.old_role_id
          AND m.old_role_id <> m.canonical_role_id;
    """)

    # Delete duplicate permission mappings.
    op.execute("""
        DELETE FROM role_permissions rp
        USING role_id_map m
        WHERE rp.role_id = m.old_role_id
          AND m.old_role_id <> m.canonical_role_id;
    """)

    # Make the three canonical roles global.
    op.execute("""
        UPDATE roles r
        SET
            workspace_id = NULL,
            created_by = NULL,
            is_system_role = TRUE
        WHERE r.role_id IN (
            SELECT DISTINCT canonical_role_id
            FROM role_id_map
        );
    """)

    # Delete duplicate role records.
    op.execute("""
        DELETE FROM roles r
        USING role_id_map m
        WHERE r.role_id = m.old_role_id
          AND m.old_role_id <> m.canonical_role_id;
    """)

    # Enforce globally unique role names.
    op.create_unique_constraint(
        "uq_global_system_role_name",
        "roles",
        ["role_name"],
    )


def downgrade() -> None:
    """This data migration cannot be safely reversed."""

    raise RuntimeError(
        "This migration merges workspace-specific roles into global roles. "
        "The original role IDs and creator information cannot be restored."
    )
