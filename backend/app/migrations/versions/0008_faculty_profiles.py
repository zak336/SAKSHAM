"""Create faculty profiles.

Revision ID: 0008
Revises: 0007
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision: str = "0008"
down_revision: str | None = "0007"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "faculty_profiles",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "tenant_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "college_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "department_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "designation",
            sa.String(length=100),
            nullable=True,
        ),
        sa.Column(
            "qualification",
            sa.String(length=255),
            nullable=True,
        ),
        sa.Column(
            "joining_date",
            sa.Date(),
            nullable=True,
        ),
        sa.Column(
            "research_interests",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "bio",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["tenants.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["college_id"],
            ["colleges.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["department_id"],
            ["departments.id"],
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "user_id",
            name="uq_faculty_profile_user",
        ),
    )

    op.create_index(
        "ix_faculty_profiles_tenant_id",
        "faculty_profiles",
        ["tenant_id"],
    )

    op.create_index(
        "ix_faculty_profiles_college_id",
        "faculty_profiles",
        ["college_id"],
    )

    op.create_index(
        "ix_faculty_profiles_department_id",
        "faculty_profiles",
        ["department_id"],
    )

    op.create_index(
        "ix_faculty_profiles_user_id",
        "faculty_profiles",
        ["user_id"],
    )


def downgrade() -> None:
    op.drop_table("faculty_profiles")