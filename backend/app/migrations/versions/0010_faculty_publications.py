"""Create faculty publications.

Revision ID: 0010
Revises: 0009
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision: str = "0010"
down_revision: str | None = "0009"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "faculty_publications",
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
            "publication_type",
            sa.String(length=50),
            nullable=False,
        ),
        sa.Column(
            "journal_or_conference",
            sa.String(length=500),
            nullable=True,
        ),
        sa.Column(
            "publisher",
            sa.String(length=255),
            nullable=True,
        ),
        sa.Column(
            "publication_date",
            sa.Date(),
            nullable=True,
        ),
        sa.Column(
            "volume",
            sa.String(length=50),
            nullable=True,
        ),
        sa.Column(
            "issue",
            sa.String(length=50),
            nullable=True,
        ),
        sa.Column(
            "pages",
            sa.String(length=100),
            nullable=True,
        ),
        sa.Column(
            "doi",
            sa.String(length=255),
            nullable=True,
        ),
        sa.Column(
            "indexing",
            sa.String(length=255),
            nullable=True,
        ),
        sa.Column(
            "url",
            sa.String(length=2048),
            nullable=True,
        ),
        sa.Column(
            "abstract",
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
        "ix_faculty_publications_tenant_id",
        "faculty_publications",
        ["tenant_id"],
    )

    op.create_index(
        "ix_faculty_publications_college_id",
        "faculty_publications",
        ["college_id"],
    )

    op.create_index(
        "ix_faculty_publications_faculty_id",
        "faculty_publications",
        ["faculty_id"],
    )

    op.create_index(
        "ix_faculty_publications_publication_type",
        "faculty_publications",
        ["publication_type"],
    )

    op.create_index(
        "ix_faculty_publications_publication_date",
        "faculty_publications",
        ["publication_date"],
    )


def downgrade() -> None:
    op.drop_table("faculty_publications")