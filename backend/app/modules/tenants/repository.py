"""Tenant repository — all DB access for the tenants module."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.tenants.models import Tenant


async def get_by_slug(db: AsyncSession, slug: str) -> Tenant | None:
    result = await db.execute(select(Tenant).where(Tenant.slug == slug))
    return result.scalar_one_or_none()


async def get_by_id(db: AsyncSession, tenant_id: uuid.UUID) -> Tenant | None:
    result = await db.execute(select(Tenant).where(Tenant.id == tenant_id))
    return result.scalar_one_or_none()


async def list_all(db: AsyncSession) -> list[Tenant]:
    result = await db.execute(select(Tenant).order_by(Tenant.name))
    return list(result.scalars().all())


async def create(db: AsyncSession, name: str, slug: str) -> Tenant:
    tenant = Tenant(id=uuid.uuid4(), name=name, slug=slug)
    db.add(tenant)
    await db.flush()
    await db.refresh(tenant)
    return tenant


async def update(
    db: AsyncSession,
    tenant: Tenant,
    name: str | None = None,
    is_active: bool | None = None,
) -> Tenant:
    if name is not None:
        tenant.name = name
    if is_active is not None:
        tenant.is_active = is_active
    await db.flush()
    await db.refresh(tenant)
    return tenant
