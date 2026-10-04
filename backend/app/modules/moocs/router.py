"""MOOC completion router."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_college, get_current_user, get_tenant
from app.modules.colleges.models import College
from app.modules.moocs import service
from app.modules.moocs.schemas import MoocCompletionCreateRequest, MoocCompletionResponse, MoocCompletionUpdateRequest
from app.modules.tenants.models import Tenant
from app.modules.users.models import User

router = APIRouter(prefix="/moocs", tags=["moocs"])


@router.post("", response_model=MoocCompletionResponse, status_code=status.HTTP_201_CREATED)
async def create_mooc(
    payload: MoocCompletionCreateRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    tenant: Annotated[Tenant, Depends(get_tenant)],
    college: Annotated[College, Depends(get_college)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> MoocCompletionResponse:
    item = await service.create(db, current_user=current_user, tenant_id=tenant.id, college_id=college.id, payload=payload)
    return MoocCompletionResponse.model_validate(item)


@router.get("/me", response_model=list[MoocCompletionResponse])
async def list_my_moocs(
    db: Annotated[AsyncSession, Depends(get_db)],
    tenant: Annotated[Tenant, Depends(get_tenant)],
    college: Annotated[College, Depends(get_college)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> list[MoocCompletionResponse]:
    items = await service.list_for_user(db, current_user=current_user, tenant_id=tenant.id, college_id=college.id, user_id=current_user.id)
    return [MoocCompletionResponse.model_validate(item) for item in items]


@router.get("/users/{user_id}", response_model=list[MoocCompletionResponse])
async def list_user_moocs(
    user_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    tenant: Annotated[Tenant, Depends(get_tenant)],
    college: Annotated[College, Depends(get_college)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> list[MoocCompletionResponse]:
    items = await service.list_for_user(db, current_user=current_user, tenant_id=tenant.id, college_id=college.id, user_id=user_id)
    return [MoocCompletionResponse.model_validate(item) for item in items]


@router.get("/{completion_id}", response_model=MoocCompletionResponse)
async def get_mooc(
    completion_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    tenant: Annotated[Tenant, Depends(get_tenant)],
    college: Annotated[College, Depends(get_college)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> MoocCompletionResponse:
    item = await service.get(db, current_user=current_user, tenant_id=tenant.id, college_id=college.id, completion_id=completion_id)
    return MoocCompletionResponse.model_validate(item)


@router.patch("/{completion_id}", response_model=MoocCompletionResponse)
async def update_mooc(
    completion_id: uuid.UUID,
    payload: MoocCompletionUpdateRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    tenant: Annotated[Tenant, Depends(get_tenant)],
    college: Annotated[College, Depends(get_college)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> MoocCompletionResponse:
    item = await service.update(db, current_user=current_user, tenant_id=tenant.id, college_id=college.id, completion_id=completion_id, payload=payload)
    return MoocCompletionResponse.model_validate(item)


@router.delete("/{completion_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_mooc(
    completion_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    tenant: Annotated[Tenant, Depends(get_tenant)],
    college: Annotated[College, Depends(get_college)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> None:
    await service.delete(db, current_user=current_user, tenant_id=tenant.id, college_id=college.id, completion_id=completion_id)
