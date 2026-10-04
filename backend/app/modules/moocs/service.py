"""MOOC completion business logic."""

import uuid

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.moocs import repository
from app.modules.moocs.models import MoocCompletion
from app.modules.moocs.schemas import MoocCompletionCreateRequest, MoocCompletionUpdateRequest
from app.modules.users.models import User, UserRole


def _forbidden(code: str, message: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail={"code": code, "message": message},
    )


async def _validate_target_user(
    db: AsyncSession,
    *,
    current_user: User,
    tenant_id: uuid.UUID,
    college_id: uuid.UUID,
    target_user_id: uuid.UUID,
) -> User:
    result = await db.execute(
        select(User).where(
            User.id == target_user_id,
            User.tenant_id == tenant_id,
            User.college_id == college_id,
            User.is_active.is_(True),
        )
    )
    user = result.scalar_one_or_none()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"code": "USER_NOT_FOUND", "message": "User not found in this college."},
        )

    if target_user_id != current_user.id and current_user.role not in {UserRole.super_admin, UserRole.admin}:
        raise _forbidden(
            "MOOC_MANAGEMENT_DENIED",
            "You can only manage your own MOOC completion records.",
        )
    return user


async def create(
    db: AsyncSession,
    *,
    current_user: User,
    tenant_id: uuid.UUID,
    college_id: uuid.UUID,
    payload: MoocCompletionCreateRequest,
) -> MoocCompletion:
    target_user_id = payload.user_id or current_user.id
    await _validate_target_user(
        db,
        current_user=current_user,
        tenant_id=tenant_id,
        college_id=college_id,
        target_user_id=target_user_id,
    )

    if payload.enrolled_on and payload.completed_on and payload.completed_on < payload.enrolled_on:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"code": "INVALID_DATE_RANGE", "message": "Completion date cannot be before enrollment date."},
        )

    return await repository.create(
        db,
        tenant_id=tenant_id,
        college_id=college_id,
        user_id=target_user_id,
        course_title=payload.course_title,
        provider=payload.provider,
        platform=payload.platform,
        course_identifier=payload.course_identifier,
        duration_hours=payload.duration_hours,
        enrolled_on=payload.enrolled_on,
        completed_on=payload.completed_on,
        certificate_id=payload.certificate_id,
        certificate_url=payload.certificate_url,
        score=payload.score,
        status=payload.status,
        description=payload.description,
    )


async def list_for_user(
    db: AsyncSession,
    *,
    current_user: User,
    tenant_id: uuid.UUID,
    college_id: uuid.UUID,
    user_id: uuid.UUID,
) -> list[MoocCompletion]:
    await _validate_target_user(
        db,
        current_user=current_user,
        tenant_id=tenant_id,
        college_id=college_id,
        target_user_id=user_id,
    )
    return await repository.list_for_user(
        db,
        user_id=user_id,
        tenant_id=tenant_id,
        college_id=college_id,
    )


async def get(
    db: AsyncSession,
    *,
    current_user: User,
    tenant_id: uuid.UUID,
    college_id: uuid.UUID,
    completion_id: uuid.UUID,
) -> MoocCompletion:
    item = await repository.get_by_id(
        db,
        completion_id=completion_id,
        tenant_id=tenant_id,
        college_id=college_id,
    )
    if item is None:
        raise HTTPException(status_code=404, detail={"code": "MOOC_NOT_FOUND", "message": "MOOC completion not found."})

    await _validate_target_user(
        db,
        current_user=current_user,
        tenant_id=tenant_id,
        college_id=college_id,
        target_user_id=item.user_id,
    )
    return item


async def update(
    db: AsyncSession,
    *,
    current_user: User,
    tenant_id: uuid.UUID,
    college_id: uuid.UUID,
    completion_id: uuid.UUID,
    payload: MoocCompletionUpdateRequest,
) -> MoocCompletion:
    item = await get(
        db,
        current_user=current_user,
        tenant_id=tenant_id,
        college_id=college_id,
        completion_id=completion_id,
    )
    values = {k: v for k, v in payload.model_dump().items() if v is not None}
    enrolled_on = values.get("enrolled_on", item.enrolled_on)
    completed_on = values.get("completed_on", item.completed_on)
    if enrolled_on and completed_on and completed_on < enrolled_on:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"code": "INVALID_DATE_RANGE", "message": "Completion date cannot be before enrollment date."},
        )
    return await repository.update(db, item, **values)


async def delete(
    db: AsyncSession,
    *,
    current_user: User,
    tenant_id: uuid.UUID,
    college_id: uuid.UUID,
    completion_id: uuid.UUID,
) -> None:
    item = await get(
        db,
        current_user=current_user,
        tenant_id=tenant_id,
        college_id=college_id,
        completion_id=completion_id,
    )
    await repository.delete(db, item)
