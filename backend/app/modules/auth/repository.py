"""Auth repository — refresh token persistence."""

import hashlib
import uuid
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.auth.models import RefreshToken


def _hash(token: str) -> str:
    """SHA-256 hash of a raw token string."""
    return hashlib.sha256(token.encode()).hexdigest()


async def store_refresh_token(
    db: AsyncSession,
    user_id: uuid.UUID,
    tenant_id: uuid.UUID,
    raw_token: str,
    expires_at: datetime,
) -> RefreshToken:
    rt = RefreshToken(
        id=uuid.uuid4(),
        user_id=user_id,
        tenant_id=tenant_id,
        token_hash=_hash(raw_token),
        expires_at=expires_at,
    )
    db.add(rt)
    await db.flush()
    return rt


async def get_valid_refresh_token(db: AsyncSession, raw_token: str) -> RefreshToken | None:
    """Return a non-revoked, non-expired refresh token record, or None."""
    from datetime import UTC

    now = datetime.now(UTC)
    result = await db.execute(
        select(RefreshToken).where(
            RefreshToken.token_hash == _hash(raw_token),
            RefreshToken.revoked.is_(False),
            RefreshToken.expires_at > now,
        )
    )
    return result.scalar_one_or_none()


async def revoke_token(db: AsyncSession, raw_token: str) -> bool:
    """Revoke a refresh token. Returns True if found and revoked."""
    rt = await get_valid_refresh_token(db, raw_token)
    if rt is None:
        return False
    rt.revoked = True
    await db.flush()
    return True


async def revoke_all_user_tokens(db: AsyncSession, user_id: uuid.UUID) -> None:
    """Revoke all active refresh tokens for a user (used on logout-all)."""
    from datetime import UTC

    now = datetime.now(UTC)
    result = await db.execute(
        select(RefreshToken).where(
            RefreshToken.user_id == user_id,
            RefreshToken.revoked.is_(False),
            RefreshToken.expires_at > now,
        )
    )
    for rt in result.scalars().all():
        rt.revoked = True
    await db.flush()
