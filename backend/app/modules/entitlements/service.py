"""Module entitlement and tenant runtime configuration services."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import NotFoundError, ValidationError
from app.modules.tenants.repository import get_by_id
from app.modules.entitlements import repository
from app.modules.entitlements.models import Module
from app.modules.entitlements.schemas import ModuleResponse, TenantBrandingResponse, TenantBrandingUpdateRequest, TenantRuntimeConfigResponse
from app.modules.tenants.models import Tenant
from app.modules.tenants.settings_model import TenantSettings


async def is_module_enabled(db: AsyncSession, tenant_id: uuid.UUID, module_key: str) -> bool:
    module = await repository.get_module_by_key(db, module_key)
    if module is None:
        return False
    if module.is_core:
        return True
    item = await repository.get_tenant_module(db, tenant_id, module.id)
    return bool(item and item.enabled)


async def runtime_config(db: AsyncSession, tenant: Tenant) -> TenantRuntimeConfigResponse:
    settings_result = await db.execute(select(TenantSettings).where(TenantSettings.tenant_id == tenant.id))
    settings = settings_result.scalar_one_or_none()
    modules = await repository.list_modules(db)
    enabled = {m.id for m, _ in await repository.list_enabled_modules(db, tenant.id)}
    return TenantRuntimeConfigResponse(
        tenant_id=tenant.id,
        branding=TenantBrandingResponse(
            name=settings.display_name if settings and settings.display_name else tenant.name,
            logo_url=settings.logo_url if settings else None,
            favicon_url=settings.favicon_url if settings else None,
            primary_color=settings.primary_color if settings else None,
            secondary_color=settings.secondary_color if settings else None,
            accent_color=settings.accent_color if settings else None,
        ),
        modules=[
            ModuleResponse(
                id=m.id, key=m.key, name=m.name, description=m.description,
                is_core=m.is_core, is_active=m.is_active,
                enabled=(m.is_core or m.id in enabled),
            )
            for m in modules
        ],
    )


async def set_module(
    db: AsyncSession, tenant_id: uuid.UUID, module_key: str, enabled: bool, config: dict
) -> ModuleResponse:
    if await get_by_id(db, tenant_id) is None:
        raise NotFoundError(f"Tenant '{tenant_id}' not found.")
    module = await repository.get_module_by_key(db, module_key)
    if module is None:
        raise NotFoundError(f"Module '{module_key}' not found.")
    if module.is_core and not enabled:
        raise ValidationError(f"Core module '{module_key}' cannot be disabled.")
    item = await repository.upsert_tenant_module(db, tenant_id, module.id, enabled, config)
    return ModuleResponse(
        id=module.id, key=module.key, name=module.name, description=module.description,
        is_core=module.is_core, is_active=module.is_active, enabled=item.enabled,
    )


async def update_branding(db: AsyncSession, tenant: Tenant, payload: TenantBrandingUpdateRequest) -> TenantRuntimeConfigResponse:
    result = await db.execute(select(TenantSettings).where(TenantSettings.tenant_id == tenant.id))
    settings = result.scalar_one_or_none()
    if settings is None:
        settings = TenantSettings(tenant_id=tenant.id)
        db.add(settings)
        await db.flush()
    for field in ("display_name", "logo_url", "favicon_url", "primary_color", "secondary_color", "accent_color"):
        value = getattr(payload, field)
        if value is not None:
            setattr(settings, field, value)
    await db.flush()
    return await runtime_config(db, tenant)

async def initialize_tenant(
    db: AsyncSession,
    tenant_id: uuid.UUID,
) -> None:
    """
    Initialize the module entitlement and branding configuration
    for a newly created tenant.

    Core modules are enabled by default.
    Optional modules are disabled by default.
    """

    tenant = await get_by_id(db, tenant_id)

    if tenant is None:
        raise NotFoundError(
            f"Tenant '{tenant_id}' not found."
        )

    # Create tenant branding/settings if it does not already exist.
    settings_result = await db.execute(
        select(TenantSettings).where(
            TenantSettings.tenant_id == tenant_id
        )
    )

    settings = settings_result.scalar_one_or_none()

    if settings is None:
        settings = TenantSettings(
            tenant_id=tenant_id,
            display_name=None,
            logo_url=None,
            favicon_url=None,
            primary_color=None,
            secondary_color=None,
            accent_color=None,
        )

        db.add(settings)

    # Create an explicit entitlement row for every active module.
    modules = await repository.list_modules(db)

    for module in modules:
        existing = await repository.get_tenant_module(
            db,
            tenant_id,
            module.id,
        )

        if existing is not None:
            continue

        await repository.upsert_tenant_module(
            db=db,
            tenant_id=tenant_id,
            module_id=module.id,
            enabled=module.is_core,
            config={},
        )

    await db.flush()