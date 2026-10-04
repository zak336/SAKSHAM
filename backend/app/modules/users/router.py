"""Users router — profile management and admin user CRUD."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_college, get_current_user, get_tenant, require_roles
from app.modules.colleges.models import College
from app.modules.tenants.models import Tenant
from app.modules.users import service
from app.modules.users.models import User, UserRole
from app.modules.users.schemas import AdminUserUpdateRequest, UserCreateRequest, UserResponse, UserUpdateRequest

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: Annotated[User, Depends(get_current_user)],
) -> UserResponse:
    """Return the authenticated user's own profile."""
    return UserResponse.model_validate(current_user)


@router.patch("/me", response_model=UserResponse)
async def update_me(
    payload: UserUpdateRequest,
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> UserResponse:
    """Update the authenticated user's own name and phone."""
    updated = await service.update_own_profile(db, current_user, payload)
    return UserResponse.model_validate(updated)


@router.get("", response_model=list[UserResponse])
async def list_users(
    db: Annotated[AsyncSession, Depends(get_db)],
    tenant: Annotated[Tenant, Depends(get_tenant)],
    college: Annotated[College, Depends(get_college)],
    _: Annotated[User, Depends(require_roles(UserRole.admin, UserRole.super_admin))],
) -> list[UserResponse]:
    """List users in the selected college."""
    users = await service.list_users(db, tenant.id, college.id)
    return [UserResponse.model_validate(u) for u in users]


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    payload: UserCreateRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    tenant: Annotated[Tenant, Depends(get_tenant)],
    college: Annotated[College, Depends(get_college)],
    current_user: Annotated[User, Depends(require_roles(UserRole.admin, UserRole.super_admin))],
) -> UserResponse:
    """Create a user in the selected college."""
    user = await service.create_user(db, tenant.id, college.id, payload)
    return UserResponse.model_validate(user)


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    tenant: Annotated[Tenant, Depends(get_tenant)],
    college: Annotated[College, Depends(get_college)],
    _: Annotated[User, Depends(require_roles(UserRole.admin, UserRole.super_admin))],
) -> UserResponse:
    """Get a user by ID in the selected college."""
    user = await service.get_user(db, user_id, tenant.id, college.id)
    return UserResponse.model_validate(user)


@router.patch("/{user_id}", response_model=UserResponse)
async def admin_update_user(
    user_id: uuid.UUID,
    payload: AdminUserUpdateRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    tenant: Annotated[Tenant, Depends(get_tenant)],
    college: Annotated[College, Depends(get_college)],
    _: Annotated[User, Depends(require_roles(UserRole.admin, UserRole.super_admin))],
) -> UserResponse:
    """Update a user's role, status, or profile within a college."""
    user = await service.admin_update_user(db, user_id, tenant.id, college.id, payload)
    return UserResponse.model_validate(user)
