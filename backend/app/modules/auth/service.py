"""Auth service — login, refresh, logout business logic."""

import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import PermissionDeniedError, ValidationError
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_password,
)
from app.modules.auth import repository as auth_repo
from app.modules.auth.schemas import AccessTokenResponse, TokenResponse
from app.modules.tenants.models import Tenant
from app.modules.users.models import User


async def _get_user_by_email(db: AsyncSession, tenant_id: uuid.UUID, email: str) -> User | None:
    result = await db.execute(
        select(User).where(
            User.tenant_id == tenant_id,
            User.email == email.lower(),
            User.is_active.is_(True),
        )
    )
    return result.scalar_one_or_none()


async def login(db: AsyncSession, email: str, password: str, tenant_slug: str) -> TokenResponse:
    # Resolve tenant
    from sqlalchemy import select as sa_select

    tenant_result = await db.execute(
        sa_select(Tenant).where(Tenant.slug == tenant_slug, Tenant.is_active.is_(True))
    )
    tenant = tenant_result.scalar_one_or_none()
    if tenant is None:
        raise ValidationError("Invalid credentials.")

    # Validate user
    user = await _get_user_by_email(db, tenant.id, email)
    if user is None or not verify_password(password, user.password_hash):
        raise ValidationError("Invalid credentials.")

    # Issue tokens
    access_token = create_access_token(
        subject=str(user.id),
        tenant_id=str(tenant.id),
        role=user.role.value,
        college_id=str(user.college_id) if user.college_id else None,
    )
    raw_refresh = create_refresh_token(
        subject=str(user.id),
        tenant_id=str(tenant.id),
    )
    expires_at = datetime.now(UTC) + timedelta(days=settings.refresh_token_expire_days)
    await auth_repo.store_refresh_token(db, user.id, tenant.id, raw_refresh, expires_at)

    return TokenResponse(
        access_token=access_token,
        refresh_token=raw_refresh,
        expires_in=settings.access_token_expire_minutes * 60,
    )


async def refresh(db: AsyncSession, raw_refresh_token: str) -> AccessTokenResponse:
    from jose import JWTError

    # Validate token signature/expiry first
    try:
        payload = decode_token(raw_refresh_token)
    except JWTError as exc:
        raise PermissionDeniedError("Invalid refresh token.") from exc

    if payload.get("type") != "refresh":
        raise PermissionDeniedError("Invalid refresh token.")

    # Validate against DB (not revoked, not expired)
    rt = await auth_repo.get_valid_refresh_token(db, raw_refresh_token)
    if rt is None:
        raise PermissionDeniedError("Refresh token has been revoked or expired.")

    # Load user
    user_id = uuid.UUID(payload["sub"])
    result = await db.execute(select(User).where(User.id == user_id, User.is_active.is_(True)))
    user = result.scalar_one_or_none()
    if user is None:
        raise PermissionDeniedError("User not found.")

    new_access = create_access_token(
        subject=str(user.id),
        tenant_id=str(user.tenant_id),
        role=user.role.value,
        college_id=str(user.college_id) if user.college_id else None,
    )
    return AccessTokenResponse(
        access_token=new_access,
        expires_in=settings.access_token_expire_minutes * 60,
    )


async def logout(db: AsyncSession, raw_refresh_token: str) -> None:
    """Revoke the given refresh token."""
    await auth_repo.revoke_token(db, raw_refresh_token)
