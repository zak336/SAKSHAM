"""Create MOOC completion records.

Revision ID: 0014
Revises: 0013
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision: str = "0014"
down_revision: str | None = "0013"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "mooc_completions",
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
            "user_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "course_title",
            sa.String(length=500),
            nullable=False,
        ),
        sa.Column(
            "provider",
            sa.String(length=255),
            nullable=True,
        ),
        sa.Column(
            "platform",
            sa.String(length=255),
            nullable=True,
        ),
        sa.Column(
            "course_identifier",
            sa.String(length=255),
            nullable=True,
        ),
        sa.Column(
            "duration_hours",
            sa.Numeric(8, 2),
            nullable=True,
        ),
        sa.Column(
            "enrolled_on",
            sa.Date(),
            nullable=True,
        ),
        sa.Column(
            "completed_on",
            sa.Date(),
            nullable=True,
        ),
        sa.Column(
            "certificate_id",
            sa.String(length=255),
            nullable=True,
        ),
        sa.Column(
            "certificate_url",
            sa.String(length=2048),
            nullable=True,
        ),
        sa.Column(
            "score",
            sa.Numeric(6, 2),
            nullable=True,
        ),
        sa.Column(
            "status",
            sa.String(length=50),
            nullable=False,
            server_default="completed",
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
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_mooc_completions_tenant_id",
        "mooc_completions",
        ["tenant_id"],
    )

    op.create_index(
        "ix_mooc_completions_college_id",
        "mooc_completions",
        ["college_id"],
    )

    op.create_index(
        "ix_mooc_completions_user_id",
        "mooc_completions",
        ["user_id"],
    )

    op.create_index(
        "ix_mooc_completions_completed_on",
        "mooc_completions",
        ["completed_on"],
    )


def downgrade() -> None:
    op.drop_table("mooc_completions")