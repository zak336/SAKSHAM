import uuid
"""Tenant module entitlements and runtime configuration."""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_tenant, require_roles
from app.modules.entitlements import repository, service
from app.modules.entitlements.schemas import ModuleResponse, TenantBrandingUpdateRequest, TenantModuleUpdateRequest, TenantRuntimeConfigResponse
from app.modules.tenants.models import Tenant
from app.modules.tenants import service as tenant_service
from app.modules.users.models import User, UserRole

router = APIRouter(tags=["configuration"])

@router.get(
    "/tenants/{tenant_id}/config",
    response_model=TenantRuntimeConfigResponse,
)
async def get_tenant_config_as_super_admin(
    tenant_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[
        User,
        Depends(require_roles(UserRole.super_admin)),
    ],
) -> TenantRuntimeConfigResponse:
    tenant = await tenant_service.get_tenant(
        db,
        tenant_id,
    )

    return await service.runtime_config(
        db,
        tenant,
    )

@router.patch(
    "/tenants/{tenant_id}/branding",
    response_model=TenantRuntimeConfigResponse,
)
async def update_tenant_branding_as_super_admin(
    tenant_id: uuid.UUID,
    payload: TenantBrandingUpdateRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[
        User,
        Depends(require_roles(UserRole.super_admin)),
    ],
) -> TenantRuntimeConfigResponse:
    tenant = await tenant_service.get_tenant(
        db,
        tenant_id,
    )

    return await service.update_branding(
        db,
        tenant,
        payload,
    )

@router.get("/config", response_model=TenantRuntimeConfigResponse)
async def get_runtime_config(
    db: Annotated[AsyncSession, Depends(get_db)],
    tenant: Annotated[Tenant, Depends(get_tenant)],
) -> TenantRuntimeConfigResponse:
    return await service.runtime_config(db, tenant)


@router.patch("/tenant/settings", response_model=TenantRuntimeConfigResponse)
async def update_tenant_branding(
    payload: TenantBrandingUpdateRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    tenant: Annotated[Tenant, Depends(get_tenant)],
    _: Annotated[User, Depends(require_roles(UserRole.admin, UserRole.super_admin))],
) -> TenantRuntimeConfigResponse:
    return await service.update_branding(db, tenant, payload)


@router.get("/modules", response_model=list[ModuleResponse])
async def list_available_modules(
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(require_roles(UserRole.super_admin))],
) -> list[ModuleResponse]:
    modules = await repository.list_modules(db)
    return [
        ModuleResponse(id=m.id, key=m.key, name=m.name, description=m.description, is_core=m.is_core, is_active=m.is_active)
        for m in modules
    ]


@router.patch("/tenants/{tenant_id}/modules/{module_key}", response_model=ModuleResponse)
async def set_tenant_module(
    tenant_id: uuid.UUID,
    module_key: str,
    payload: TenantModuleUpdateRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(require_roles(UserRole.super_admin))],
) -> ModuleResponse:
    return await service.set_module(db, tenant_id, module_key, payload.enabled, payload.config)
