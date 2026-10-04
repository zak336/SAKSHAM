"""Create faculty course assignments.

Revision ID: 0013
Revises: 0012
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision: str = "0013"
down_revision: str | None = "0012"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "faculty_course_assignments",
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
            "faculty_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "course_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "academic_year",
            sa.String(length=20),
            nullable=False,
        ),
        sa.Column(
            "semester",
            sa.Integer(),
            nullable=False,
        ),
        sa.Column(
            "section",
            sa.String(length=50),
            nullable=True,
        ),
        sa.Column(
            "teaching_role",
            sa.String(length=50),
            nullable=False,
            server_default="primary",
        ),
        sa.Column(
            "assigned_from",
            sa.Date(),
            nullable=True,
        ),
        sa.Column(
            "assigned_until",
            sa.Date(),
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
            ["faculty_id"],
            ["faculty_profiles.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["course_id"],
            ["courses.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_faculty_course_assignments_tenant_id",
        "faculty_course_assignments",
        ["tenant_id"],
    )

    op.create_index(
        "ix_faculty_course_assignments_college_id",
        "faculty_course_assignments",
        ["college_id"],
    )

    op.create_index(
        "ix_faculty_course_assignments_faculty_id",
        "faculty_course_assignments",
        ["faculty_id"],
    )

    op.create_index(
        "ix_faculty_course_assignments_course_id",
        "faculty_course_assignments",
        ["course_id"],
    )

    op.create_index(
        "ix_faculty_course_assignments_academic_year",
        "faculty_course_assignments",
        ["academic_year"],
    )


def downgrade() -> None:
    op.drop_table("faculty_course_assignments")