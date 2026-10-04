"""Department scope service."""

import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.exceptions import ConflictError, NotFoundError, ValidationError
from app.modules.departments.models import Department
from app.modules.user_scope import repository
from app.modules.user_scope.models import UserDepartment
from app.modules.user_scope.schemas import UserDepartmentCreateRequest
from app.modules.users.models import User, UserRole

_SCOPE_ROLES = {UserRole.faculty, UserRole.hod}


async def assign_department(db: AsyncSession, tenant_id: uuid.UUID, college_id: uuid.UUID, user_id: uuid.UUID, payload: UserDepartmentCreateRequest) -> UserDepartment:
    user_result = await db.execute(select(User).where(User.id == user_id, User.tenant_id == tenant_id, User.college_id == college_id, User.role.in_(_SCOPE_ROLES), User.is_active.is_(True)))
    if user_result.scalar_one_or_none() is None:
        raise ValidationError("Faculty/HOD user not found in this tenant.")
    dept_result = await db.execute(select(Department).where(Department.id == payload.department_id, Department.tenant_id == tenant_id, Department.college_id == college_id, Department.is_active.is_(True)))
    if dept_result.scalar_one_or_none() is None:
        raise ValidationError("Department not found in this tenant.")
    if await repository.get_assignment(db, tenant_id, user_id, college_id, payload.department_id):
        raise ConflictError("User is already assigned to this department.")
    return await repository.create(db, tenant_id, college_id, user_id, payload.department_id, payload.is_primary)


async def list_assignments(db: AsyncSession, tenant_id: uuid.UUID, college_id: uuid.UUID, user_id: uuid.UUID) -> list[UserDepartment]:
    return await repository.list_assignments(db, tenant_id, college_id, user_id)


async def remove_assignment(db: AsyncSession, tenant_id: uuid.UUID, college_id: uuid.UUID, user_id: uuid.UUID, department_id: uuid.UUID) -> None:
    item = await repository.get_assignment(db, tenant_id, user_id, college_id, department_id)
    if item is None:
        raise NotFoundError("User department assignment not found.")
    await repository.delete(db, item)
