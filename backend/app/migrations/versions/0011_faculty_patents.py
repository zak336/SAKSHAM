"""Create faculty patents.

Revision ID: 0011
Revises: 0010
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision: str = "0011"
down_revision: str | None = "0010"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "faculty_patents",
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
            "patent_number",
            sa.String(length=255),
            nullable=True,
        ),
        sa.Column(
            "application_number",
            sa.String(length=255),
            nullable=True,
        ),
        sa.Column(
            "patent_type",
            sa.String(length=50),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.String(length=50),
            nullable=False,
        ),
        sa.Column(
            "filing_date",
            sa.Date(),
            nullable=True,
        ),
        sa.Column(
            "publication_date",
            sa.Date(),
            nullable=True,
        ),
        sa.Column(
            "grant_date",
            sa.Date(),
            nullable=True,
        ),
        sa.Column(
            "inventors",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "assignee",
            sa.String(length=500),
            nullable=True,
        ),
        sa.Column(
            "country",
            sa.String(length=100),
            nullable=True,
        ),
        sa.Column(
            "office",
            sa.String(length=255),
            nullable=True,
        ),
        sa.Column(
            "description",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "reference_url",
            sa.String(length=2048),
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
        "ix_faculty_patents_tenant_id",
        "faculty_patents",
        ["tenant_id"],
    )

    op.create_index(
        "ix_faculty_patents_college_id",
        "faculty_patents",
        ["college_id"],
    )

    op.create_index(
        "ix_faculty_patents_faculty_id",
        "faculty_patents",
        ["faculty_id"],
    )

    op.create_index(
        "ix_faculty_patents_status",
        "faculty_patents",
        ["status"],
    )

    op.create_index(
        "ix_faculty_patents_filing_date",
        "faculty_patents",
        ["filing_date"],
    )


def downgrade() -> None:
    op.drop_table("faculty_patents")