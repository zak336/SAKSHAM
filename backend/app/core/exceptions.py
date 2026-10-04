"""Typed domain exceptions and global FastAPI exception handlers."""

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

# ─── Domain exceptions ────────────────────────────────────────────────────────


class ZakCERPError(Exception):
    """Base exception for all ZakCERP domain errors."""


class TenantNotFoundError(ZakCERPError):
    """Raised when the X-Tenant-ID header resolves to no known tenant."""


class PermissionDeniedError(ZakCERPError):
    """Raised when the authenticated user lacks the required role."""


class NotFoundError(ZakCERPError):
    """Raised when a requested resource does not exist."""


class ConflictError(ZakCERPError):
    """Raised when a unique constraint would be violated."""


class ValidationError(ZakCERPError):
    """Raised when business-rule validation fails (distinct from schema validation)."""


# ─── Handlers ─────────────────────────────────────────────────────────────────


def _error_body(code: str, message: str) -> dict[str, object]:
    return {"success": False, "error": {"code": code, "message": message}}


def register_exception_handlers(app: FastAPI) -> None:
    """Attach all domain exception handlers to the FastAPI app."""

    @app.exception_handler(TenantNotFoundError)
    async def tenant_not_found(_req: Request, exc: TenantNotFoundError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=_error_body("TENANT_NOT_FOUND", str(exc) or "Tenant not found"),
        )

    @app.exception_handler(PermissionDeniedError)
    async def permission_denied(_req: Request, exc: PermissionDeniedError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content=_error_body("PERMISSION_DENIED", str(exc) or "Permission denied"),
        )

    @app.exception_handler(NotFoundError)
    async def not_found(_req: Request, exc: NotFoundError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content=_error_body("NOT_FOUND", str(exc) or "Resource not found"),
        )

    @app.exception_handler(ConflictError)
    async def conflict(_req: Request, exc: ConflictError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_409_CONFLICT,
            content=_error_body("CONFLICT", str(exc) or "Resource already exists"),
        )

    @app.exception_handler(ValidationError)
    async def validation_error(_req: Request, exc: ValidationError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=_error_body("VALIDATION_ERROR", str(exc)),
        )
