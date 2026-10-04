"""User service scoped to a tenant and college."""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import ConflictError, NotFoundError, ValidationError
from app.modules.users import repository
from app.modules.users.models import User, UserRole
from app.modules.users.schemas import AdminUserUpdateRequest, UserCreateRequest, UserUpdateRequest


async def create_user(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    college_id: uuid.UUID,
    payload: UserCreateRequest,
) -> User:
    existing = await repository.get_by_email(db, payload.email, tenant_id)
    if existing is not None:
        raise ConflictError(f"A user with email '{payload.email}' already exists in this tenant.")

    assigned_college = None if payload.role == UserRole.super_admin else college_id
    if payload.role != UserRole.super_admin and assigned_college is None:
        raise ValidationError("A college is required for tenant users.")

    return await repository.create(
        db,
        tenant_id=tenant_id,
        college_id=assigned_college,
        name=payload.name,
        email=payload.email,
        password=payload.password,
        role=payload.role,
        phone=payload.phone,
    )


async def get_user(
    db: AsyncSession, user_id: uuid.UUID, tenant_id: uuid.UUID, college_id: uuid.UUID | None = None
) -> User:
    user = await repository.get_by_id(db, user_id, tenant_id, college_id)
    if user is None:
        raise NotFoundError(f"User '{user_id}' not found.")
    return user


async def list_users(
    db: AsyncSession, tenant_id: uuid.UUID, college_id: uuid.UUID | None = None
) -> list[User]:
    return await repository.list_by_tenant(db, tenant_id, college_id)


async def update_own_profile(db: AsyncSession, user: User, payload: UserUpdateRequest) -> User:
    return await repository.update(db, user, name=payload.name, phone=payload.phone)


async def admin_update_user(
    db: AsyncSession,
    user_id: uuid.UUID,
    tenant_id: uuid.UUID,
    college_id: uuid.UUID,
    payload: AdminUserUpdateRequest,
) -> User:
    user = await get_user(db, user_id, tenant_id, college_id)
    return await repository.update(
        db,
        user,
        name=payload.name,
        phone=payload.phone,
        role=payload.role,
        is_active=payload.is_active,
        college_id=college_id,
    )
