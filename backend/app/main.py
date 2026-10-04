"""ZakCERP FastAPI application factory."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.core.exceptions import register_exception_handlers
from app.core.redis import close_redis
from app.modules.academics.router import router as academics_router
from app.modules.attendance.router import router as attendance_router
from app.modules.entitlements.router import router as entitlements_router
from app.modules.user_scope.router import router as user_scope_router

# Module routers
from app.modules.auth.router import router as auth_router
from app.modules.colleges.router import router as colleges_router, my_college_router
from app.modules.courses.router import router as courses_router
from app.modules.departments.router import router as departments_router
from app.modules.notices.router import router as notices_router
from app.modules.placements.router import router as placements_router
from app.modules.results.router import router as results_router
from app.modules.students.router import router as students_router
from app.modules.tenants.router import router as tenants_router
from app.modules.timetable.router import router as timetable_router
from app.modules.users.router import router as users_router
from app.modules.faculty.router import router as faculty_router
from app.modules.moocs.router import router as moocs_router

# Routers
from app.routers.health import router as health_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manage startup and shutdown events."""
    # Startup: nothing to do yet (DB migrations run via Alembic before start)
    yield
    # Shutdown: close connection pools
    await close_redis()


def create_app() -> FastAPI:
    app = FastAPI(
        title="ZakCERP API",
        description="Multi-tenant College ERP platform",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

    # ── CORS ──────────────────────────────────────────────────────────────────
    # In development, allow all origins so Flutter web (Chrome) works without
    # needing to know the exact dev server port.
    is_dev = settings.app_env == "development"
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"] if is_dev else settings.cors_origins_list,
        allow_credentials=not is_dev,  # credentials=True incompatible with wildcard
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Exception handlers ────────────────────────────────────────────────────
    register_exception_handlers(app)

    # ── Routes ────────────────────────────────────────────────────────────────
    app.include_router(health_router)

    api_prefix = "/api/v1"
    app.include_router(auth_router, prefix=api_prefix)
    app.include_router(tenants_router, prefix=api_prefix)
    app.include_router(colleges_router, prefix=api_prefix)
    app.include_router(my_college_router, prefix=api_prefix)
    app.include_router(users_router, prefix=api_prefix)
    app.include_router(departments_router, prefix=api_prefix)
    app.include_router(courses_router, prefix=api_prefix)
    app.include_router(students_router, prefix=api_prefix)
    app.include_router(attendance_router, prefix=api_prefix)
    app.include_router(entitlements_router, prefix=api_prefix)
    app.include_router(user_scope_router, prefix=api_prefix)
    app.include_router(academics_router, prefix=api_prefix)
    app.include_router(placements_router, prefix=api_prefix)
    app.include_router(timetable_router, prefix=api_prefix)
    app.include_router(notices_router, prefix=api_prefix)
    app.include_router(results_router, prefix=api_prefix)
    app.include_router(faculty_router, prefix=api_prefix)
    app.include_router(moocs_router, prefix=api_prefix)

    @app.get("/", tags=["root"], summary="Root")
    async def root() -> dict[str, str]:
        return {"message": "Hello, ZakCERP"}

    return app


app = create_app()
