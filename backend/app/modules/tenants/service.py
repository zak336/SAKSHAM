"""Tenant service — business logic for tenant management."""
import uuid
from app.modules.entitlements import service as entitlements_service

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, NotFoundError
from app.modules.tenants import repository
from app.modules.tenants.models import Tenant
from app.modules.tenants.schemas import TenantCreateRequest, TenantUpdateRequest


async def create_tenant(
    db: AsyncSession,
    payload: TenantCreateRequest,
) -> Tenant:
    existing = await repository.get_by_slug(db, payload.slug)

    if existing is not None:
        raise ConflictError(
            f"A tenant with slug '{payload.slug}' already exists."
        )

    tenant = await repository.create(
        db,
        name=payload.name,
        slug=payload.slug,
    )

    await entitlements_service.initialize_tenant(db, tenant.id)

    return tenant

async def get_tenant(db: AsyncSession, tenant_id: uuid.UUID) -> Tenant:
    tenant = await repository.get_by_id(db, tenant_id)
    if tenant is None:
        raise NotFoundError(f"Tenant '{tenant_id}' not found.")
    return tenant


async def list_tenants(db: AsyncSession) -> list[Tenant]:
    return await repository.list_all(db)


async def update_tenant(
    db: AsyncSession, tenant_id: uuid.UUID, payload: TenantUpdateRequest
) -> Tenant:
    tenant = await get_tenant(db, tenant_id)
    return await repository.update(db, tenant, name=payload.name, is_active=payload.is_active)
