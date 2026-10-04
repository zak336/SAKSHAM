"""Create faculty development program records.

Revision ID: 0015
Revises: 0014
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision: str = "0015"
down_revision: str | None = "0014"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "faculty_development_programs",
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
            "title",
            sa.String(length=500),
            nullable=False,
        ),
        sa.Column(
            "organizer",
            sa.String(length=500),
            nullable=True,
        ),
        sa.Column(
            "program_type",
            sa.String(length=100),
            nullable=True,
        ),
        sa.Column(
            "mode",
            sa.String(length=50),
            nullable=True,
        ),
        sa.Column(
            "venue",
            sa.String(length=500),
            nullable=True,
        ),
        sa.Column(
            "start_date",
            sa.Date(),
            nullable=True,
        ),
        sa.Column(
            "end_date",
            sa.Date(),
            nullable=True,
        ),
        sa.Column(
            "duration_hours",
            sa.Numeric(8, 2),
            nullable=True,
        ),
        sa.Column(
            "certificate_number",
            sa.String(length=255),
            nullable=True,
        ),
        sa.Column(
            "certificate_url",
            sa.String(length=2048),
            nullable=True,
        ),
        sa.Column(
            "description",
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
            ["faculty_id"],
            ["faculty_profiles.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_faculty_development_programs_tenant_id",
        "faculty_development_programs",
        ["tenant_id"],
    )

    op.create_index(
        "ix_faculty_development_programs_college_id",
        "faculty_development_programs",
        ["college_id"],
    )

    op.create_index(
        "ix_faculty_development_programs_faculty_id",
        "faculty_development_programs",
        ["faculty_id"],
    )

    op.create_index(
        "ix_faculty_development_programs_start_date",
        "faculty_development_programs",
        ["start_date"],
    )


def downgrade() -> None:
    op.drop_table("faculty_development_programs")