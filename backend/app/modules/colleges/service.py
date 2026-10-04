"""College management business logic."""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, NotFoundError
from app.modules.colleges import repository
from app.modules.colleges.models import College
from app.modules.colleges.schemas import CollegeCreateRequest, CollegeUpdateRequest
from app.modules.tenants import service as tenant_service


async def create_college(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    payload: CollegeCreateRequest,
) -> College:
    await tenant_service.get_tenant(db, tenant_id)
    if await repository.get_by_slug(db, tenant_id, payload.slug) is not None:
        raise ConflictError(f"College with slug '{payload.slug}' already exists in this tenant.")
    if await repository.get_by_code(db, tenant_id, payload.code) is not None:
        raise ConflictError(f"College with code '{payload.code}' already exists in this tenant.")
    return await repository.create(
        db,
        tenant_id=tenant_id,
        name=payload.name,
        code=payload.code,
        slug=payload.slug,
    )


async def get_college(
    db: AsyncSession, tenant_id: uuid.UUID, college_id: uuid.UUID
) -> College:
    await tenant_service.get_tenant(db, tenant_id)
    college = await repository.get_by_id(db, tenant_id, college_id)
    if college is None:
        raise NotFoundError(f"College '{college_id}' not found in this tenant.")
    return college


async def list_colleges(db: AsyncSession, tenant_id: uuid.UUID) -> list[College]:
    await tenant_service.get_tenant(db, tenant_id)
    return await repository.list_by_tenant(db, tenant_id)


async def update_college(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    college_id: uuid.UUID,
    payload: CollegeUpdateRequest,
) -> College:
    college = await get_college(db, tenant_id, college_id)
    if payload.code is not None:
        existing = await repository.get_by_code(db, tenant_id, payload.code)
        if existing is not None and existing.id != college.id:
            raise ConflictError(f"College with code '{payload.code}' already exists in this tenant.")
    return await repository.update(
        db,
        college,
        name=payload.name,
        code=payload.code,
        is_active=payload.is_active,
    )
