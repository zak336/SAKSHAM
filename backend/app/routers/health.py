"""Health check endpoints — no auth required."""

from typing import Annotated

from fastapi import APIRouter, Depends, Header
from pydantic import BaseModel
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.redis import get_redis

router = APIRouter(tags=["health"])


class HealthResponse(BaseModel):
    status: str
    tenant: str
    database: str
    redis: str


@router.get("/health", response_model=HealthResponse, summary="Service health check")
async def health_check(
    db: Annotated[AsyncSession, Depends(get_db)],
    x_tenant_id: Annotated[str | None, Header(alias="X-Tenant-ID")] = None,
) -> HealthResponse:
    """
    Returns the health status of the API and its dependencies.
    No authentication required.
    """
    # Check database connectivity
    try:
        await db.execute(text("SELECT 1"))
        db_status = "ok"
    except Exception:
        db_status = "unreachable"

    # Check Redis connectivity
    try:
        redis = await get_redis()
        await redis.ping()
        redis_status = "ok"
    except Exception:
        redis_status = "unreachable"

    return HealthResponse(
        status="ok",
        tenant=x_tenant_id or "none",
        database=db_status,
        redis=redis_status,
    )
