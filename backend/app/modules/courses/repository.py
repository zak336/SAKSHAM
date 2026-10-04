"""Course repository scoped to tenant and college."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.courses.models import Course


async def get_by_id(
    db: AsyncSession, course_id: uuid.UUID, tenant_id: uuid.UUID, college_id: uuid.UUID
) -> Course | None:
    result = await db.execute(
        select(Course).where(
            Course.id == course_id,
            Course.tenant_id == tenant_id,
            Course.college_id == college_id,
        )
    )
    return result.scalar_one_or_none()


async def list_by_tenant(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    college_id: uuid.UUID,
    department_id: uuid.UUID | None = None,
    semester: int | None = None,
    department_ids: set[uuid.UUID] | None = None,
) -> list[Course]:
    query = select(Course).where(
        Course.tenant_id == tenant_id,
        Course.college_id == college_id,
    )
    if department_ids is not None:
        query = query.where(Course.department_id.in_(department_ids))
    if department_id is not None:
        query = query.where(Course.department_id == department_id)
    if semester is not None:
        query = query.where(Course.semester == semester)
    query = query.order_by(Course.semester, Course.code)
    result = await db.execute(query)
    return list(result.scalars().all())


async def create(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    college_id: uuid.UUID,
    department_id: uuid.UUID,
    name: str,
    code: str,
    semester: int,
    credits: int,
    faculty_id: uuid.UUID | None = None,
) -> Course:
    course = Course(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        college_id=college_id,
        department_id=department_id,
        name=name,
        code=code.upper(),
        semester=semester,
        credits=credits,
        faculty_id=faculty_id,
    )
    db.add(course)
    await db.flush()
    await db.refresh(course)
    return course


async def update(
    db: AsyncSession,
    course: Course,
    name: str | None = None,
    faculty_id: uuid.UUID | None = None,
    credits: int | None = None,
    is_active: bool | None = None,
) -> Course:
    if name is not None:
        course.name = name
    if faculty_id is not None:
        course.faculty_id = faculty_id
    if credits is not None:
        course.credits = credits
    if is_active is not None:
        course.is_active = is_active
    await db.flush()
    await db.refresh(course)
    return course
