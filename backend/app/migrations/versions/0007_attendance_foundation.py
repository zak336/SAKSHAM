"""Create course enrollments and attendance tables.

Revision ID: 0007
Revises: 0006
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision: str = "0007"
down_revision: str | None = "0006"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # ---------------------------------------------------------
    # Course enrollments
    # ---------------------------------------------------------
    op.create_table(
        "course_enrollments",
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
            "course_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "student_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "created_at",
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
            ["course_id"],
            ["courses.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["student_id"],
            ["students.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "college_id",
            "course_id",
            "student_id",
            name="uq_course_enrollment",
        ),
    )

    op.create_index(
        "ix_course_enrollments_tenant_id",
        "course_enrollments",
        ["tenant_id"],
    )
    op.create_index(
        "ix_course_enrollments_college_id",
        "course_enrollments",
        ["college_id"],
    )
    op.create_index(
        "ix_course_enrollments_course_id",
        "course_enrollments",
        ["course_id"],
    )
    op.create_index(
        "ix_course_enrollments_student_id",
        "course_enrollments",
        ["student_id"],
    )

    # ---------------------------------------------------------
    # Attendance sessions
    # ---------------------------------------------------------
    op.create_table(
        "attendance_sessions",
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
            "course_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "faculty_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "held_on",
            sa.Date(),
            nullable=False,
        ),
        sa.Column(
            "period",
            sa.Integer(),
            nullable=False,
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
            ["course_id"],
            ["courses.id"],
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["faculty_id"],
            ["users.id"],
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "college_id",
            "course_id",
            "held_on",
            "period",
            name="uq_attendance_session",
        ),
    )

    op.create_index(
        "ix_attendance_sessions_tenant_id",
        "attendance_sessions",
        ["tenant_id"],
    )
    op.create_index(
        "ix_attendance_sessions_college_id",
        "attendance_sessions",
        ["college_id"],
    )
    op.create_index(
        "ix_attendance_sessions_course_id",
        "attendance_sessions",
        ["course_id"],
    )
    op.create_index(
        "ix_attendance_sessions_faculty_id",
        "attendance_sessions",
        ["faculty_id"],
    )
    op.create_index(
        "ix_attendance_sessions_held_on",
        "attendance_sessions",
        ["held_on"],
    )

    # ---------------------------------------------------------
    # Attendance records
    # ---------------------------------------------------------
    op.create_table(
        "attendance_records",
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
            "session_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "student_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.String(length=20),
            nullable=False,
        ),
        sa.Column(
            "marked_at",
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
            ["session_id"],
            ["attendance_sessions.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["student_id"],
            ["students.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "session_id",
            "student_id",
            name="uq_attendance_record",
        ),
    )

    op.create_index(
        "ix_attendance_records_tenant_id",
        "attendance_records",
        ["tenant_id"],
    )
    op.create_index(
        "ix_attendance_records_college_id",
        "attendance_records",
        ["college_id"],
    )
    op.create_index(
        "ix_attendance_records_session_id",
        "attendance_records",
        ["session_id"],
    )
    op.create_index(
        "ix_attendance_records_student_id",
        "attendance_records",
        ["student_id"],
    )

    # Basic database-level status validation.
    op.create_check_constraint(
        "ck_attendance_record_status",
        "attendance_records",
        "status IN ('present', 'absent', 'late', 'excused')",
    )


def downgrade() -> None:
    op.drop_constraint(
        "ck_attendance_record_status",
        "attendance_records",
        type_="check",
    )

    op.drop_table("attendance_records")
    op.drop_table("attendance_sessions")
    op.drop_table("course_enrollments")