"""Tenants router — super_admin only."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import require_roles
from app.modules.tenants import service
from app.modules.tenants.schemas import (
    TenantCreateRequest,
    TenantResponse,
    TenantUpdateRequest,
)
from app.modules.users.models import User, UserRole

router = APIRouter(prefix="/tenants", tags=["tenants"])


@router.post("", response_model=TenantResponse, status_code=status.HTTP_201_CREATED)
async def create_tenant(
    payload: TenantCreateRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(require_roles(UserRole.super_admin))],
) -> TenantResponse:
    """Create a new tenant college. Super admin only."""
    tenant = await service.create_tenant(db, payload)
    return TenantResponse.model_validate(tenant)


@router.get("", response_model=list[TenantResponse])
async def list_tenants(
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(require_roles(UserRole.super_admin))],
) -> list[TenantResponse]:
    """List all tenants. Super admin only."""
    tenants = await service.list_tenants(db)
    return [TenantResponse.model_validate(t) for t in tenants]


@router.get("/{tenant_id}", response_model=TenantResponse)
async def get_tenant(
    tenant_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(require_roles(UserRole.super_admin))],
) -> TenantResponse:
    """Get a single tenant. Super admin only."""
    tenant = await service.get_tenant(db, tenant_id)
    return TenantResponse.model_validate(tenant)


@router.patch("/{tenant_id}", response_model=TenantResponse)
async def update_tenant(
    tenant_id: uuid.UUID,
    payload: TenantUpdateRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(require_roles(UserRole.super_admin))],
) -> TenantResponse:
    """Update a tenant. Super admin only."""
    tenant = await service.update_tenant(db, tenant_id, payload)
    return TenantResponse.model_validate(tenant)
