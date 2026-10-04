"""Department repository scoped to tenant and college."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.departments.models import Department


async def get_by_id(
    db: AsyncSession, dept_id: uuid.UUID, tenant_id: uuid.UUID, college_id: uuid.UUID
) -> Department | None:
    result = await db.execute(
        select(Department).where(
            Department.id == dept_id,
            Department.tenant_id == tenant_id,
            Department.college_id == college_id,
        )
    )
    return result.scalar_one_or_none()


async def get_by_code(
    db: AsyncSession, code: str, tenant_id: uuid.UUID, college_id: uuid.UUID
) -> Department | None:
    result = await db.execute(
        select(Department).where(
            Department.code == code.upper(),
            Department.tenant_id == tenant_id,
            Department.college_id == college_id,
        )
    )
    return result.scalar_one_or_none()


async def list_by_tenant(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    college_id: uuid.UUID,
    department_ids: set[uuid.UUID] | None = None,
) -> list[Department]:
    query = select(Department).where(
        Department.tenant_id == tenant_id,
        Department.college_id == college_id,
    )
    if department_ids is not None:
        query = query.where(Department.id.in_(department_ids))
    query = query.order_by(Department.name)
    result = await db.execute(query)
    return list(result.scalars().all())


async def create(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    college_id: uuid.UUID,
    name: str,
    code: str,
) -> Department:
    dept = Department(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        college_id=college_id,
        name=name,
        code=code.upper(),
    )
    db.add(dept)
    await db.flush()
    await db.refresh(dept)
    return dept


async def update(
    db: AsyncSession,
    dept: Department,
    name: str | None = None,
    is_active: bool | None = None,
) -> Department:
    if name is not None:
        dept.name = name
    if is_active is not None:
        dept.is_active = is_active
    await db.flush()
    await db.refresh(dept)
    return dept
