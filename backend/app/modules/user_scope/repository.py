"""Department scope repository."""

import uuid
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.modules.user_scope.models import UserDepartment


async def get_assignment(db: AsyncSession, tenant_id: uuid.UUID, user_id: uuid.UUID, college_id: uuid.UUID, department_id: uuid.UUID) -> UserDepartment | None:
    result = await db.execute(select(UserDepartment).where(
        UserDepartment.tenant_id == tenant_id,
        UserDepartment.user_id == user_id,
        UserDepartment.college_id == college_id,
        UserDepartment.department_id == department_id,
    ))
    return result.scalar_one_or_none()


async def list_assignments(db: AsyncSession, tenant_id: uuid.UUID, college_id: uuid.UUID, user_id: uuid.UUID) -> list[UserDepartment]:
    result = await db.execute(select(UserDepartment).where(
        UserDepartment.tenant_id == tenant_id,
        UserDepartment.user_id == user_id,
        UserDepartment.college_id == college_id,
    ).order_by(UserDepartment.is_primary.desc()))
    return list(result.scalars().all())


async def department_ids(db: AsyncSession, tenant_id: uuid.UUID, college_id: uuid.UUID, user_id: uuid.UUID) -> set[uuid.UUID]:
    return {item.department_id for item in await list_assignments(db, tenant_id, college_id, user_id)}


async def create(db: AsyncSession, tenant_id: uuid.UUID, college_id: uuid.UUID, user_id: uuid.UUID, department_id: uuid.UUID, is_primary: bool) -> UserDepartment:
    item = UserDepartment(id=uuid.uuid4(), tenant_id=tenant_id, college_id=college_id, user_id=user_id, department_id=department_id, is_primary=is_primary)
    db.add(item)
    await db.flush()
    await db.refresh(item)
    return item


async def delete(db: AsyncSession, item: UserDepartment) -> None:
    await db.delete(item)
    await db.flush()
