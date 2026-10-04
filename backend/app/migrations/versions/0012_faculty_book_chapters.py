"""Create faculty book chapters.

Revision ID: 0012
Revises: 0011
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision: str = "0012"
down_revision: str | None = "0011"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "faculty_book_chapters",
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
            "chapter_title",
            sa.String(length=500),
            nullable=False,
        ),
        sa.Column(
            "book_title",
            sa.String(length=500),
            nullable=False,
        ),
        sa.Column(
            "publisher",
            sa.String(length=500),
            nullable=True,
        ),
        sa.Column(
            "publication_date",
            sa.Date(),
            nullable=True,
        ),
        sa.Column(
            "isbn",
            sa.String(length=100),
            nullable=True,
        ),
        sa.Column(
            "edition",
            sa.String(length=100),
            nullable=True,
        ),
        sa.Column(
            "chapter_number",
            sa.String(length=50),
            nullable=True,
        ),
        sa.Column(
            "pages",
            sa.String(length=100),
            nullable=True,
        ),
        sa.Column(
            "editors",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "doi",
            sa.String(length=255),
            nullable=True,
        ),
        sa.Column(
            "url",
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
        "ix_faculty_book_chapters_tenant_id",
        "faculty_book_chapters",
        ["tenant_id"],
    )

    op.create_index(
        "ix_faculty_book_chapters_college_id",
        "faculty_book_chapters",
        ["college_id"],
    )

    op.create_index(
        "ix_faculty_book_chapters_faculty_id",
        "faculty_book_chapters",
        ["faculty_id"],
    )

    op.create_index(
        "ix_faculty_book_chapters_publication_date",
        "faculty_book_chapters",
        ["publication_date"],
    )


def downgrade() -> None:
    op.drop_table("faculty_book_chapters")