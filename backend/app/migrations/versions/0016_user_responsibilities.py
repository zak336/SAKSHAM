"""Add user_responsibilities table for Faculty + HOD model.

Revision ID: 0016
Revises: 0015
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0016"
down_revision: str | None = "0015"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Create user_responsibilities table and backfill from existing users.role."""
    
    # Create table
    op.create_table(
        "user_responsibilities",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("college_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("responsibility", sa.String(length=50), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("starts_at", sa.Date(), nullable=True),
        sa.Column("ends_at", sa.Date(), nullable=True),
        sa.Column("assigned_by", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.func.now(),
            nullable=False
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.func.now(),
            nullable=False
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id"],
            ["tenants.id"],
            ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["college_id"],
            ["colleges.id"],
            ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["assigned_by"],
            ["users.id"],
            ondelete="SET NULL"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    
    # Create indexes
    op.create_index(
        "ix_user_responsibilities_tenant_id",
        "user_responsibilities",
        ["tenant_id"]
    )
    op.create_index(
        "ix_user_responsibilities_college_id",
        "user_responsibilities",
        ["college_id"]
    )
    op.create_index(
        "ix_user_responsibilities_user_id",
        "user_responsibilities",
        ["user_id"]
    )
    op.create_index(
        "ix_user_responsibilities_responsibility",
        "user_responsibilities",
        ["responsibility"]
    )
    op.create_index(
        "ix_user_responsibilities_is_active",
        "user_responsibilities",
        ["is_active"]
    )
    
    # Create unique constraint for active responsibilities
    # PostgreSQL partial unique index
    op.execute(
        """
        CREATE UNIQUE INDEX uq_user_responsibility_active
        ON user_responsibilities (tenant_id, college_id, user_id, responsibility)
        WHERE is_active = true
        """
    )
    
    # Backfill: Create responsibility records for existing faculty and hod users
    # This is deterministic and safe because:
    # 1. Faculty users with role='faculty' get 'faculty' responsibility
    # 2. HOD users with role='hod' get 'hod' responsibility  
    # 3. Super admins are excluded (no college_id)
    # 4. Other roles are not backfilled (student, admin, etc. don't need responsibilities yet)
    
    op.execute(
        """
        INSERT INTO user_responsibilities (
            id,
            tenant_id,
            college_id,
            user_id,
            responsibility,
            is_active,
            starts_at,
            created_at,
            updated_at
        )
        SELECT
            gen_random_uuid(),
            u.tenant_id,
            u.college_id,
            u.id,
            u.role,  -- 'faculty' or 'hod' directly from role field
            true,
            CURRENT_DATE,
            NOW(),
            NOW()
        FROM users u
        WHERE u.role IN ('faculty', 'hod')
          AND u.college_id IS NOT NULL
          AND u.is_active = true
        ON CONFLICT DO NOTHING
        """
    )


def downgrade() -> None:
    """Drop user_responsibilities table."""
    
    # Drop indexes
    op.execute("DROP INDEX IF EXISTS uq_user_responsibility_active")
    op.drop_index("ix_user_responsibilities_is_active", table_name="user_responsibilities")
    op.drop_index("ix_user_responsibilities_responsibility", table_name="user_responsibilities")
    op.drop_index("ix_user_responsibilities_user_id", table_name="user_responsibilities")
    op.drop_index("ix_user_responsibilities_college_id", table_name="user_responsibilities")
    op.drop_index("ix_user_responsibilities_tenant_id", table_name="user_responsibilities")
    
    # Drop table
    op.drop_table("user_responsibilities")
