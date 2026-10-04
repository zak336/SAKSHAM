"""College repository."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.colleges.models import College


async def get_by_id(
    db: AsyncSession, tenant_id: uuid.UUID, college_id: uuid.UUID
) -> College | None:
    result = await db.execute(
        select(College).where(
            College.id == college_id,
            College.tenant_id == tenant_id,
        )
    )
    return result.scalar_one_or_none()


async def get_by_slug(
    db: AsyncSession, tenant_id: uuid.UUID, slug: str
) -> College | None:
    result = await db.execute(
        select(College).where(
            College.tenant_id == tenant_id,
            College.slug == slug.lower(),
        )
    )
    return result.scalar_one_or_none()


async def get_by_code(
    db: AsyncSession, tenant_id: uuid.UUID, code: str
) -> College | None:
    result = await db.execute(
        select(College).where(
            College.tenant_id == tenant_id,
            College.code == code.upper(),
        )
    )
    return result.scalar_one_or_none()


async def list_by_tenant(
    db: AsyncSession, tenant_id: uuid.UUID
) -> list[College]:
    result = await db.execute(
        select(College)
        .where(College.tenant_id == tenant_id)
        .order_by(College.name)
    )
    return list(result.scalars().all())


async def create(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    name: str,
    code: str,
    slug: str,
) -> College:
    college = College(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        name=name,
        code=code.upper(),
        slug=slug.lower(),
    )
    db.add(college)
    await db.flush()
    await db.refresh(college)
    return college


async def update(
    db: AsyncSession,
    college: College,
    name: str | None = None,
    code: str | None = None,
    is_active: bool | None = None,
) -> College:
    if name is not None:
        college.name = name
    if code is not None:
        college.code = code.upper()
    if is_active is not None:
        college.is_active = is_active
    await db.flush()
    await db.refresh(college)
    return college
