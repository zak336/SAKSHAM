"""Repository for module catalog and tenant entitlements."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.entitlements.models import Module, TenantModule


async def list_modules(db: AsyncSession) -> list[Module]:
    result = await db.execute(select(Module).where(Module.is_active.is_(True)).order_by(Module.name))
    return list(result.scalars().all())


async def get_module_by_key(db: AsyncSession, key: str) -> Module | None:
    result = await db.execute(select(Module).where(Module.key == key, Module.is_active.is_(True)))
    return result.scalar_one_or_none()


async def get_tenant_module(db: AsyncSession, tenant_id: uuid.UUID, module_id: uuid.UUID) -> TenantModule | None:
    result = await db.execute(select(TenantModule).where(TenantModule.tenant_id == tenant_id, TenantModule.module_id == module_id))
    return result.scalar_one_or_none()


async def list_enabled_modules(db: AsyncSession, tenant_id: uuid.UUID) -> list[tuple[Module, TenantModule]]:
    result = await db.execute(
        select(Module, TenantModule)
        .join(TenantModule, TenantModule.module_id == Module.id)
        .where(TenantModule.tenant_id == tenant_id, TenantModule.enabled.is_(True), Module.is_active.is_(True))
        .order_by(Module.name)
    )
    return list(result.all())


async def upsert_tenant_module(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    module_id: uuid.UUID,
    enabled: bool,
    config: dict,
) -> TenantModule:
    item = await get_tenant_module(db, tenant_id, module_id)
    now = datetime.now(timezone.utc)
    if item is None:
        item = TenantModule(
            id=uuid.uuid4(), tenant_id=tenant_id, module_id=module_id,
            enabled=enabled, config=config,
            enabled_at=now if enabled else None,
            disabled_at=None if enabled else now,
        )
        db.add(item)
    else:
        item.enabled = enabled
        item.config = config
        item.enabled_at = now if enabled else item.enabled_at
        item.disabled_at = now if not enabled else None
    await db.flush()
    await db.refresh(item)
    return item
