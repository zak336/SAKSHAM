"""Department service."""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, NotFoundError
from app.modules.departments import repository
from app.modules.departments.models import Department
from app.modules.departments.schemas import DepartmentCreateRequest, DepartmentUpdateRequest


async def create_department(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    college_id: uuid.UUID,
    payload: DepartmentCreateRequest,
) -> Department:
    existing = await repository.get_by_code(db, payload.code, tenant_id, college_id)
    if existing is not None:
        raise ConflictError(f"Department with code '{payload.code}' already exists in this college.")
    return await repository.create(db, tenant_id, college_id, payload.name, payload.code)


async def get_department(
    db: AsyncSession,
    dept_id: uuid.UUID,
    tenant_id: uuid.UUID,
    college_id: uuid.UUID,
) -> Department:
    dept = await repository.get_by_id(db, dept_id, tenant_id, college_id)
    if dept is None:
        raise NotFoundError(f"Department '{dept_id}' not found.")
    return dept


async def list_departments(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    college_id: uuid.UUID,
    department_ids: set[uuid.UUID] | None = None,
) -> list[Department]:
    return await repository.list_by_tenant(db, tenant_id, college_id, department_ids=department_ids)


async def update_department(
    db: AsyncSession,
    dept_id: uuid.UUID,
    tenant_id: uuid.UUID,
    college_id: uuid.UUID,
    payload: DepartmentUpdateRequest,
) -> Department:
    dept = await get_department(db, dept_id, tenant_id, college_id)
    return await repository.update(db, dept, name=payload.name, is_active=payload.is_active)
