"""Course service."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, NotFoundError, ValidationError
from app.modules.courses import repository
from app.modules.courses.models import Course
from app.modules.courses.schemas import CourseCreateRequest, CourseUpdateRequest
from app.modules.departments import repository as dept_repo
from app.modules.users.models import User, UserRole


async def create_course(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    college_id: uuid.UUID,
    payload: CourseCreateRequest,
) -> Course:
    dept = await dept_repo.get_by_id(db, payload.department_id, tenant_id, college_id)
    if dept is None:
        raise ValidationError("Department not found in this college.")

    existing = await repository.list_by_tenant(db, tenant_id, college_id, semester=payload.semester)
    if any(c.code == payload.code.upper() for c in existing):
        raise ConflictError(
            f"Course '{payload.code}' already exists in semester {payload.semester}."
        )

    if payload.faculty_id is not None:
        result = await db.execute(
            select(User).where(
                User.id == payload.faculty_id,
                User.tenant_id == tenant_id,
                User.college_id == college_id,
                User.role.in_([UserRole.faculty, UserRole.hod]),
                User.is_active.is_(True),
            )
        )
        if result.scalar_one_or_none() is None:
            raise ValidationError("Faculty user not found in this college.")

    return await repository.create(
        db,
        tenant_id=tenant_id,
        college_id=college_id,
        department_id=payload.department_id,
        name=payload.name,
        code=payload.code,
        semester=payload.semester,
        credits=payload.credits,
        faculty_id=payload.faculty_id,
    )


async def get_course(
    db: AsyncSession, course_id: uuid.UUID, tenant_id: uuid.UUID, college_id: uuid.UUID
) -> Course:
    course = await repository.get_by_id(db, course_id, tenant_id, college_id)
    if course is None:
        raise NotFoundError(f"Course '{course_id}' not found.")
    return course


async def list_courses(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    college_id: uuid.UUID,
    department_id: uuid.UUID | None = None,
    semester: int | None = None,
    department_ids: set[uuid.UUID] | None = None,
) -> list[Course]:
    return await repository.list_by_tenant(
        db,
        tenant_id,
        college_id,
        department_id=department_id,
        semester=semester,
        department_ids=department_ids,
    )


async def update_course(
    db: AsyncSession,
    course_id: uuid.UUID,
    tenant_id: uuid.UUID,
    college_id: uuid.UUID,
    payload: CourseUpdateRequest,
) -> Course:
    course = await get_course(db, course_id, tenant_id, college_id)
    return await repository.update(
        db,
        course,
        name=payload.name,
        faculty_id=payload.faculty_id,
        credits=payload.credits,
        is_active=payload.is_active,
    )
