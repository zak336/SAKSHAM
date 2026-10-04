"""MOOC completion repository."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.moocs.models import MoocCompletion


async def get_by_id(
    db: AsyncSession,
    *,
    completion_id: uuid.UUID,
    tenant_id: uuid.UUID,
    college_id: uuid.UUID,
) -> MoocCompletion | None:
    result = await db.execute(
        select(MoocCompletion).where(
            MoocCompletion.id == completion_id,
            MoocCompletion.tenant_id == tenant_id,
            MoocCompletion.college_id == college_id,
        )
    )
    return result.scalar_one_or_none()


async def list_for_user(
    db: AsyncSession,
    *,
    user_id: uuid.UUID,
    tenant_id: uuid.UUID,
    college_id: uuid.UUID,
) -> list[MoocCompletion]:
    result = await db.execute(
        select(MoocCompletion)
        .where(
            MoocCompletion.user_id == user_id,
            MoocCompletion.tenant_id == tenant_id,
            MoocCompletion.college_id == college_id,
        )
        .order_by(
            MoocCompletion.completed_on.desc().nullslast(),
            MoocCompletion.created_at.desc(),
        )
    )
    return list(result.scalars().all())


async def create(
    db: AsyncSession,
    *,
    tenant_id: uuid.UUID,
    college_id: uuid.UUID,
    user_id: uuid.UUID,
    course_title: str,
    provider: str | None,
    platform: str | None,
    course_identifier: str | None,
    duration_hours: float | None,
    enrolled_on,
    completed_on,
    certificate_id: str | None,
    certificate_url: str | None,
    score: float | None,
    status: str,
    description: str | None,
) -> MoocCompletion:
    item = MoocCompletion(
        tenant_id=tenant_id,
        college_id=college_id,
        user_id=user_id,
        course_title=course_title,
        provider=provider,
        platform=platform,
        course_identifier=course_identifier,
        duration_hours=duration_hours,
        enrolled_on=enrolled_on,
        completed_on=completed_on,
        certificate_id=certificate_id,
        certificate_url=certificate_url,
        score=score,
        status=status,
        description=description,
    )
    db.add(item)
    await db.flush()
    await db.refresh(item)
    return item


async def update(
    db: AsyncSession,
    item: MoocCompletion,
    **values,
) -> MoocCompletion:
    for key, value in values.items():
        if value is not None:
            setattr(item, key, value)
    await db.flush()
    await db.refresh(item)
    return item


async def delete(
    db: AsyncSession,
    item: MoocCompletion,
) -> None:
    await db.delete(item)
    await db.flush()
