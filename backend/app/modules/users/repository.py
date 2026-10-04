"""User repository scoped to tenant and optional college."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.modules.users.models import User, UserRole


async def get_by_id(
    db: AsyncSession, user_id: uuid.UUID, tenant_id: uuid.UUID, college_id: uuid.UUID | None = None
) -> User | None:
    query = select(User).where(User.id == user_id, User.tenant_id == tenant_id)
    if college_id is not None:
        query = query.where(User.college_id == college_id)
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def get_by_email(db: AsyncSession, email: str, tenant_id: uuid.UUID) -> User | None:
    result = await db.execute(
        select(User).where(User.email == email.lower(), User.tenant_id == tenant_id)
    )
    return result.scalar_one_or_none()


async def list_by_tenant(
    db: AsyncSession, tenant_id: uuid.UUID, college_id: uuid.UUID | None = None
) -> list[User]:
    query = select(User).where(User.tenant_id == tenant_id)
    if college_id is not None:
        query = query.where(User.college_id == college_id)
    result = await db.execute(query.order_by(User.name))
    return list(result.scalars().all())


async def create(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    college_id: uuid.UUID | None,
    name: str,
    email: str,
    password: str,
    role: UserRole,
    phone: str | None = None,
) -> User:
    user = User(
        id=uuid.uuid4(),
        tenant_id=tenant_id,
        college_id=college_id,
        name=name,
        email=email.lower(),
        password_hash=hash_password(password),
        role=role,
        phone=phone,
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)
    return user


async def update(
    db: AsyncSession,
    user: User,
    name: str | None = None,
    phone: str | None = None,
    role: UserRole | None = None,
    is_active: bool | None = None,
    college_id: uuid.UUID | None = None,
) -> User:
    if name is not None:
        user.name = name
    if phone is not None:
        user.phone = phone
    if role is not None:
        user.role = role
        user.college_id = None if role == UserRole.super_admin else college_id
    elif college_id is not None:
        user.college_id = college_id
    if is_active is not None:
        user.is_active = is_active
    await db.flush()
    await db.refresh(user)
    return user
