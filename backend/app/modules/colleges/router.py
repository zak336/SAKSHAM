"""College management endpoints."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import require_roles, get_current_user, get_db
from app.core.exceptions import NotFoundError
from app.modules.colleges import service
from app.modules.colleges.schemas import CollegeCreateRequest, CollegeResponse, CollegeUpdateRequest
from app.modules.users.models import User, UserRole

router = APIRouter(prefix="/tenants/{tenant_id}/colleges", tags=["colleges"])
my_college_router = APIRouter(
    prefix="/colleges",
    tags=["colleges"],
)

_manager_roles = require_roles(UserRole.super_admin)


@router.post("", response_model=CollegeResponse, status_code=status.HTTP_201_CREATED)
async def create_college(
    tenant_id: uuid.UUID,
    payload: CollegeCreateRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(_manager_roles)],
) -> CollegeResponse:
    """Create a college under a tenant. Super admin only."""
    college = await service.create_college(db, tenant_id, payload)
    return CollegeResponse.model_validate(college)


@router.get("", response_model=list[CollegeResponse])
async def list_colleges(
    tenant_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(_manager_roles)],
) -> list[CollegeResponse]:
    """List all colleges belonging to a tenant. Super admin only."""
    colleges = await service.list_colleges(db, tenant_id)
    return [CollegeResponse.model_validate(college) for college in colleges]


@router.get("/{college_id}", response_model=CollegeResponse)
async def get_college(
    tenant_id: uuid.UUID,
    college_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(_manager_roles)],
) -> CollegeResponse:
    """Get a college under a tenant. Super admin only."""
    college = await service.get_college(db, tenant_id, college_id)
    return CollegeResponse.model_validate(college)


@router.patch("/{college_id}", response_model=CollegeResponse)
async def update_college(
    tenant_id: uuid.UUID,
    college_id: uuid.UUID,
    payload: CollegeUpdateRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    _: Annotated[User, Depends(_manager_roles)],
) -> CollegeResponse:
    """Update a college under a tenant. Super admin only."""
    college = await service.update_college(db, tenant_id, college_id, payload)
    return CollegeResponse.model_validate(college)

@my_college_router.get(
    "/me",
    response_model=CollegeResponse,
)
async def get_my_college(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> CollegeResponse:
    if current_user.college_id is None:
        raise NotFoundError(
            "Authenticated user is not assigned to a college."
        )

    college = await service.get_college(
        db,
        current_user.tenant_id,
        current_user.college_id,
    )

    return CollegeResponse.model_validate(college)