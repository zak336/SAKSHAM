"""Add the tenant -> college hierarchy and scope existing academic data.

Revision ID: 0006
Revises: ef1bf6250002
"""

from collections.abc import Sequence
import re
import uuid

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0006"
down_revision: str | None = "ef1bf6250002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _college_slug(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug[:100] or "main-college"


def _college_code(value: str) -> str:
    code = re.sub(r"[^A-Z0-9]+", "", value.upper())
    return (code[:30] or "COLLEGE")


def upgrade() -> None:
    op.create_table(
        "colleges",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("code", sa.String(length=30), nullable=False),
        sa.Column("slug", sa.String(length=100), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "code", name="uq_college_tenant_code"),
        sa.UniqueConstraint("tenant_id", "slug", name="uq_college_tenant_slug"),
    )
    op.create_index("ix_colleges_tenant_id", "colleges", ["tenant_id"])
    op.create_index("ix_colleges_slug", "colleges", ["slug"])

    op.create_table(
        "college_settings",
        sa.Column("college_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("display_name", sa.String(length=255), nullable=True),
        sa.Column("logo_url", sa.String(length=2048), nullable=True),
        sa.Column("favicon_url", sa.String(length=2048), nullable=True),
        sa.Column("primary_color", sa.String(length=20), nullable=True),
        sa.Column("secondary_color", sa.String(length=20), nullable=True),
        sa.Column("accent_color", sa.String(length=20), nullable=True),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(["college_id"], ["colleges.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("college_id"),
    )


    op.add_column("users", sa.Column("college_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column("departments", sa.Column("college_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column("courses", sa.Column("college_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column("students", sa.Column("college_id", postgresql.UUID(as_uuid=True), nullable=True))
    op.add_column("user_departments", sa.Column("college_id", postgresql.UUID(as_uuid=True), nullable=True))

    op.create_index("ix_users_college_id", "users", ["college_id"])
    op.create_index("ix_departments_college_id", "departments", ["college_id"])
    op.create_index("ix_courses_college_id", "courses", ["college_id"])
    op.create_index("ix_students_college_id", "students", ["college_id"])
    op.create_index("ix_user_departments_college_id", "user_departments", ["college_id"])

    op.create_foreign_key("fk_users_college_id", "users", "colleges", ["college_id"], ["id"], ondelete="SET NULL")
    op.create_foreign_key("fk_departments_college_id", "departments", "colleges", ["college_id"], ["id"], ondelete="RESTRICT")
    op.create_foreign_key("fk_courses_college_id", "courses", "colleges", ["college_id"], ["id"], ondelete="RESTRICT")
    op.create_foreign_key("fk_students_college_id", "students", "colleges", ["college_id"], ["id"], ondelete="RESTRICT")
    op.create_foreign_key("fk_user_departments_college_id", "user_departments", "colleges", ["college_id"], ["id"], ondelete="CASCADE")

    # Create one initial college per existing tenant. This preserves all
    # existing tenant data while introducing the new hierarchy.
    tenants = op.get_bind().execute(sa.text("SELECT id, name, slug FROM tenants ORDER BY created_at")).mappings().all()
    for tenant in tenants:
        college_id = uuid.uuid4()
        base_name = tenant["name"]
        slug = _college_slug(tenant["slug"])
        code = _college_code(tenant["slug"])

        existing = op.get_bind().execute(
            sa.text(
                "SELECT id FROM colleges WHERE tenant_id = :tenant_id AND slug = :slug"
            ),
            {"tenant_id": tenant["id"], "slug": slug},
        ).scalar_one_or_none()
        if existing is None:
            op.get_bind().execute(
                sa.text(
                    "INSERT INTO colleges (id, tenant_id, name, code, slug, is_active) "
                    "VALUES (:id, :tenant_id, :name, :code, :slug, true)"
                ),
                {
                    "id": college_id,
                    "tenant_id": tenant["id"],
                    "name": base_name,
                    "code": code,
                    "slug": slug,
                },
            )
        else:
            college_id = existing

        op.get_bind().execute(
            sa.text("UPDATE users SET college_id = :college_id WHERE tenant_id = :tenant_id AND role <> 'super_admin' AND college_id IS NULL"),
            {"tenant_id": tenant["id"], "college_id": college_id},
        )
        op.get_bind().execute(
            sa.text("UPDATE departments SET college_id = :college_id WHERE tenant_id = :tenant_id AND college_id IS NULL"),
            {"tenant_id": tenant["id"], "college_id": college_id},
        )
        op.get_bind().execute(
            sa.text("UPDATE courses SET college_id = :college_id WHERE tenant_id = :tenant_id AND college_id IS NULL"),
            {"tenant_id": tenant["id"], "college_id": college_id},
        )
        op.get_bind().execute(
            sa.text("UPDATE students SET college_id = :college_id WHERE tenant_id = :tenant_id AND college_id IS NULL"),
            {"tenant_id": tenant["id"], "college_id": college_id},
        )
        op.get_bind().execute(
            sa.text("UPDATE user_departments SET college_id = :college_id WHERE tenant_id = :tenant_id AND college_id IS NULL"),
            {"tenant_id": tenant["id"], "college_id": college_id},
        )

    op.execute(sa.text("INSERT INTO college_settings (college_id) SELECT id FROM colleges ON CONFLICT DO NOTHING"))

    # Keep tenant_id as the hard isolation boundary, but enforce college scope
    # for all existing college-owned records.
    op.create_check_constraint(
        "ck_users_non_super_admin_college",
        "users",
        "role = 'super_admin' OR college_id IS NOT NULL",
    )
    op.create_check_constraint(
        "ck_departments_college_required",
        "departments",
        "college_id IS NOT NULL",
    )
    op.create_check_constraint(
        "ck_courses_college_required",
        "courses",
        "college_id IS NOT NULL",
    )
    op.create_check_constraint(
        "ck_students_college_required",
        "students",
        "college_id IS NOT NULL",
    )
    op.create_check_constraint(
        "ck_user_departments_college_required",
        "user_departments",
        "college_id IS NOT NULL",
    )

    op.drop_constraint("uq_dept_tenant_code", "departments", type_="unique")
    op.create_unique_constraint("uq_department_college_code", "departments", ["college_id", "code"])

    op.drop_constraint("uq_course_tenant_code_semester", "courses", type_="unique")
    op.create_unique_constraint("uq_course_college_code_semester", "courses", ["college_id", "code", "semester"])

    op.drop_constraint("uq_student_tenant_roll", "students", type_="unique")
    op.create_unique_constraint("uq_student_college_roll", "students", ["college_id", "roll_number"])


def downgrade() -> None:
    op.drop_constraint("uq_student_college_roll", "students", type_="unique")
    op.create_unique_constraint("uq_student_tenant_roll", "students", ["tenant_id", "roll_number"])

    op.drop_constraint("uq_course_college_code_semester", "courses", type_="unique")
    op.create_unique_constraint("uq_course_tenant_code_semester", "courses", ["tenant_id", "code", "semester"])

    op.drop_constraint("uq_department_college_code", "departments", type_="unique")
    op.create_unique_constraint("uq_dept_tenant_code", "departments", ["tenant_id", "code"])

    for name, table in [
        ("ck_user_departments_college_required", "user_departments"),
        ("ck_students_college_required", "students"),
        ("ck_courses_college_required", "courses"),
        ("ck_departments_college_required", "departments"),
        ("ck_users_non_super_admin_college", "users"),
    ]:
        op.drop_constraint(name, table, type_="check")

    op.drop_constraint("fk_user_departments_college_id", "user_departments", type_="foreignkey")
    op.drop_constraint("fk_students_college_id", "students", type_="foreignkey")
    op.drop_constraint("fk_courses_college_id", "courses", type_="foreignkey")
    op.drop_constraint("fk_departments_college_id", "departments", type_="foreignkey")
    op.drop_constraint("fk_users_college_id", "users", type_="foreignkey")

    for table, index in [
        ("user_departments", "ix_user_departments_college_id"),
        ("students", "ix_students_college_id"),
        ("courses", "ix_courses_college_id"),
        ("departments", "ix_departments_college_id"),
        ("users", "ix_users_college_id"),
    ]:
        op.drop_index(index, table_name=table)

    for table in ["user_departments", "students", "courses", "departments", "users"]:
        op.drop_column(table, "college_id")

    op.drop_table("college_settings")
    op.drop_index("ix_colleges_slug", table_name="colleges")
    op.drop_index("ix_colleges_tenant_id", table_name="colleges")
    op.drop_table("colleges")
