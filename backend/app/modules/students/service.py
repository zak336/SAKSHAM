"""Student service."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, NotFoundError, ValidationError
from app.modules.departments import repository as dept_repo
from app.modules.students import repository
from app.modules.students.models import Student
from app.modules.students.schemas import StudentCreateRequest, StudentDetailResponse, StudentUpdateRequest
from app.modules.users.models import User, UserRole


async def create_student(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    college_id: uuid.UUID,
    payload: StudentCreateRequest,
) -> Student:
    user_result = await db.execute(
        select(User).where(
            User.id == payload.user_id,
            User.tenant_id == tenant_id,
            User.college_id == college_id,
            User.role == UserRole.student,
            User.is_active.is_(True),
        )
    )
    if user_result.scalar_one_or_none() is None:
        raise ValidationError("Student user not found in this college.")

    dept = await dept_repo.get_by_id(db, payload.department_id, tenant_id, college_id)
    if dept is None:
        raise ValidationError("Department not found in this college.")

    if await repository.get_by_user_id(db, payload.user_id, tenant_id, college_id) is not None:
        raise ConflictError("This user already has a student profile.")
    if await repository.get_by_roll(db, payload.roll_number, tenant_id, college_id) is not None:
        raise ConflictError(f"Roll number '{payload.roll_number}' is already taken.")

    return await repository.create(
        db,
        tenant_id=tenant_id,
        college_id=college_id,
        user_id=payload.user_id,
        department_id=payload.department_id,
        roll_number=payload.roll_number,
        batch_year=payload.batch_year,
        current_semester=payload.current_semester,
    )


async def get_student(
    db: AsyncSession, student_id: uuid.UUID, tenant_id: uuid.UUID, college_id: uuid.UUID
) -> Student:
    student = await repository.get_by_id(db, student_id, tenant_id, college_id)
    if student is None:
        raise NotFoundError(f"Student '{student_id}' not found.")
    return student


async def list_students(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    college_id: uuid.UUID,
    department_id: uuid.UUID | None = None,
    semester: int | None = None,
    batch_year: int | None = None,
    department_ids: set[uuid.UUID] | None = None,
) -> list[Student]:
    return await repository.list_by_tenant(
        db,
        tenant_id,
        college_id,
        department_id=department_id,
        semester=semester,
        batch_year=batch_year,
        department_ids=department_ids,
    )


async def get_student_detail(
    db: AsyncSession, student_id: uuid.UUID, tenant_id: uuid.UUID, college_id: uuid.UUID
) -> StudentDetailResponse:
    student = await get_student(db, student_id, tenant_id, college_id)

    user_result = await db.execute(
        select(User).where(
            User.id == student.user_id,
            User.tenant_id == tenant_id,
            User.college_id == college_id,
        )
    )
    user = user_result.scalar_one()

    from app.modules.departments.models import Department
    dept_result = await db.execute(
        select(Department).where(
            Department.id == student.department_id,
            Department.tenant_id == tenant_id,
            Department.college_id == college_id,
        )
    )
    dept = dept_result.scalar_one()

    return StudentDetailResponse(
        id=student.id,
        tenant_id=student.tenant_id,
        college_id=student.college_id,
        user_id=student.user_id,
        department_id=student.department_id,
        roll_number=student.roll_number,
        batch_year=student.batch_year,
        current_semester=student.current_semester,
        student_name=user.name,
        email=user.email,
        department_name=dept.name,
        department_code=dept.code,
    )


async def update_student(
    db: AsyncSession,
    student_id: uuid.UUID,
    tenant_id: uuid.UUID,
    college_id: uuid.UUID,
    payload: StudentUpdateRequest,
) -> Student:
    student = await get_student(db, student_id, tenant_id, college_id)
    if payload.department_id is not None:
        dept = await dept_repo.get_by_id(db, payload.department_id, tenant_id, college_id)
        if dept is None:
            raise ValidationError("Department not found in this college.")
    if payload.roll_number is not None and payload.roll_number != student.roll_number:
        if await repository.get_by_roll(db, payload.roll_number, tenant_id, college_id) is not None:
            raise ConflictError(f"Roll number '{payload.roll_number}' is already taken.")
    return await repository.update(
        db,
        student,
        department_id=payload.department_id,
        current_semester=payload.current_semester,
        roll_number=payload.roll_number,
    )
