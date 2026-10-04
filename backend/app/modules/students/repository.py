"""Student repository scoped to tenant and college."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.students.models import Student


async def get_by_id(
    db: AsyncSession, student_id: uuid.UUID, tenant_id: uuid.UUID, college_id: uuid.UUID
) -> Student | None:
    result = await db.execute(
        select(Student).where(
            Student.id == student_id,
            Student.tenant_id == tenant_id,
            Student.college_id == college_id,
        )
    )
    return result.scalar_one_or_none()


async def get_by_user_id(
    db: AsyncSession, user_id: uuid.UUID, tenant_id: uuid.UUID, college_id: uuid.UUID
) -> Student | None:
    result = await db.execute(
        select(Student).where(
            Student.user_id == user_id,
            Student.tenant_id == tenant_id,
            Student.college_id == college_id,
        )
    )
    return result.scalar_one_or_none()


async def get_by_roll(
    db: AsyncSession, roll_number: str, tenant_id: uuid.UUID, college_id: uuid.UUID
) -> Student | None:
    result = await db.execute(
        select(Student).where(
            Student.roll_number == roll_number,
            Student.tenant_id == tenant_id,
            Student.college_id == college_id,
        )
    )
    return result.scalar_one_or_none()


async def list_by_tenant(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    college_id: uuid.UUID,
    department_id: uuid.UUID | None = None,
    semester: int | None = None,
    batch_year: int | None = None,
    department_ids: set[uuid.UUID] | None = None,
) -> list[Student]:
    query = select(Student).where(
        Student.tenant_id == tenant_id,
        Student.college_id == college_id,
    )
    if department_ids is not None:
        query = query.where(Student.department_id.in_(department_ids))
    if department_id is not None:
        query = query.where(Student.department_id == department_id)
    if semester is not None:
        query = query.where(Student.current_semester == semester)
    if batch_year is not None:
        query = query.where(Student.batch_year == batch_year)
    query = query.order_by(Student.roll_number)
    result = await db.execute(query)
    return list(result.scalars().all())


async def create(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    college_id: uuid.UUID,
    user_id: uuid.UUID,
    department_id: uuid.UUID,
    roll_number: str,
    batch_year: int,
    current_semester: int,
) -> Student:
    student = Student(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        college_id=college_id,
        user_id=user_id,
        department_id=department_id,
        roll_number=roll_number,
        batch_year=batch_year,
        current_semester=current_semester,
    )
    db.add(student)
    await db.flush()
    await db.refresh(student)
    return student


async def update(
    db: AsyncSession,
    student: Student,
    department_id: uuid.UUID | None = None,
    current_semester: int | None = None,
    roll_number: str | None = None,
) -> Student:
    if department_id is not None:
        student.department_id = department_id
    if current_semester is not None:
        student.current_semester = current_semester
    if roll_number is not None:
        student.roll_number = roll_number
    await db.flush()
    await db.refresh(student)
    return student
