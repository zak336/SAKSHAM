"""Add tenant branding, module entitlements, and department scopes.

Revision ID: 0004
Revises: 0003
"""

from collections.abc import Sequence
import uuid

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0004"
down_revision: str | None = "0003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


MODULES = [
    ("students", "Students", "Student profiles and academic identity", True),
    ("departments", "Departments", "College department management", True),
    ("courses", "Courses", "Course catalog and academic subjects", True),
    ("attendance", "Attendance", "Attendance marking, summaries and reports", False),
    ("marks", "Marks", "Internal marks, assessments and marksheets", False),
    ("timetable", "Timetable", "Class and faculty timetables", False),
    ("documents", "Course Files", "Syllabus, notes, lab files and academic documents", False),
    ("labs", "Labs", "Laboratory details, experiments and records", False),
    ("examinations", "Examinations", "Exam schedules, admit cards and results", False),
    ("library", "Library", "Library catalog, circulation and fines", False),
    ("notices", "Notices", "College and department notices", False),
    ("placements", "Placements", "Placement drives and student placement workflows", False),
    ("fees", "Fees", "Fees, invoices and payment records", False),
    ("hostel", "Hostel", "Hostel allocation and management", False),
    ("transport", "Transport", "College transport and routes", False),
]


def upgrade() -> None:
    # HOD is a scoped tenant role, unlike super_admin which is platform-wide.
    op.execute("ALTER TYPE userrole ADD VALUE IF NOT EXISTS 'hod'")

    op.create_table(
        "tenant_settings",
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("display_name", sa.String(255), nullable=True),
        sa.Column("logo_url", sa.String(2048), nullable=True),
        sa.Column("favicon_url", sa.String(2048), nullable=True),
        sa.Column("primary_color", sa.String(20), nullable=True),
        sa.Column("secondary_color", sa.String(20), nullable=True),
        sa.Column("accent_color", sa.String(20), nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("tenant_id"),
    )

    op.create_table(
        "modules",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("key", sa.String(100), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_core", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("key"),
    )
    op.create_index("ix_modules_key", "modules", ["key"])

    op.create_table(
        "tenant_modules",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("module_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("enabled", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("config", postgresql.JSONB(), server_default="{}", nullable=False),
        sa.Column("enabled_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("disabled_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["module_id"], ["modules.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "module_id", name="uq_tenant_module"),
    )
    op.create_index("ix_tenant_modules_tenant_id", "tenant_modules", ["tenant_id"])
    op.create_index("ix_tenant_modules_module_id", "tenant_modules", ["module_id"])

    op.create_table(
        "user_departments",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("department_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("is_primary", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["department_id"], ["departments.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "user_id", "department_id", name="uq_user_department"),
    )
    op.create_index("ix_user_departments_tenant_id", "user_departments", ["tenant_id"])
    op.create_index("ix_user_departments_user_id", "user_departments", ["user_id"])
    op.create_index("ix_user_departments_department_id", "user_departments", ["department_id"])

    modules_table = sa.table(
        "modules",
        sa.column("id", postgresql.UUID(as_uuid=True)),
        sa.column("key", sa.String()),
        sa.column("name", sa.String()),
        sa.column("description", sa.Text()),
        sa.column("is_core", sa.Boolean()),
    )
    op.bulk_insert(
        modules_table,
        [
            {"id": uuid.uuid4(), "key": key, "name": name, "description": desc, "is_core": core}
            for key, name, desc, core in MODULES
        ],
    )

    settings_table = sa.table(
        "tenant_settings",
        sa.column("tenant_id", postgresql.UUID(as_uuid=True)),
    )
    op.execute(sa.text("INSERT INTO tenant_settings (tenant_id) SELECT id FROM tenants ON CONFLICT DO NOTHING"))


def downgrade() -> None:
    op.drop_table("user_departments")
    op.drop_table("tenant_modules")
    op.drop_table("modules")
    op.drop_table("tenant_settings")
