"""Courses router."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_college, get_department_scope, get_tenant, require_department_access, require_module, require_roles
from app.modules.colleges.models import College
from app.modules.courses import service
from app.modules.courses.schemas import CourseCreateRequest, CourseResponse, CourseUpdateRequest
from app.modules.tenants.models import Tenant
from app.modules.user_scope.repository import get_assignment
from app.modules.users.models import User, UserRole

_module_access = require_module("courses")
router = APIRouter(prefix="/courses", tags=["courses"], dependencies=[Depends(_module_access)])
_admin_roles = require_roles(UserRole.admin, UserRole.super_admin)
_staff_roles = require_roles(UserRole.admin, UserRole.super_admin, UserRole.faculty, UserRole.hod)


@router.post("", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
async def create_course(
    payload: CourseCreateRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    tenant: Annotated[Tenant, Depends(get_tenant)],
    college: Annotated[College, Depends(get_college)],
    _: Annotated[User, Depends(_admin_roles)],
) -> CourseResponse:
    course = await service.create_course(db, tenant.id, college.id, payload)
    return CourseResponse.model_validate(course)


@router.get("", response_model=list[CourseResponse])
async def list_courses(
    db: Annotated[AsyncSession, Depends(get_db)],
    tenant: Annotated[Tenant, Depends(get_tenant)],
    college: Annotated[College, Depends(get_college)],
    _: Annotated[User, Depends(require_roles(UserRole.admin, UserRole.super_admin, UserRole.faculty, UserRole.hod, UserRole.student))],
    department_id: uuid.UUID | None = Query(None),
    semester: int | None = Query(None),
    department_scope: Annotated[set[uuid.UUID] | None, Depends(get_department_scope)] = None,
) -> list[CourseResponse]:
    courses = await service.list_courses(
        db,
        tenant.id,
        college.id,
        department_id=department_id,
        semester=semester,
        department_ids=department_scope,
    )
    return [CourseResponse.model_validate(c) for c in courses]


@router.get("/{course_id}", response_model=CourseResponse)
async def get_course(
    course_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    tenant: Annotated[Tenant, Depends(get_tenant)],
    college: Annotated[College, Depends(get_college)],
    current_user: Annotated[User, Depends(_staff_roles)],
) -> CourseResponse:
    course = await service.get_course(db, course_id, tenant.id, college.id)
    if current_user.role in {UserRole.faculty, UserRole.hod}:
        if await get_assignment(db, tenant.id, current_user.id, college.id, course.department_id) is None:
            raise HTTPException(
                status_code=403,
                detail={"code": "DEPARTMENT_ACCESS_DENIED", "message": "You do not have access to this course."},
            )
    return CourseResponse.model_validate(course)


@router.patch("/{course_id}", response_model=CourseResponse)
async def update_course(
    course_id: uuid.UUID,
    payload: CourseUpdateRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    tenant: Annotated[Tenant, Depends(get_tenant)],
    college: Annotated[College, Depends(get_college)],
    _: Annotated[User, Depends(_admin_roles)],
) -> CourseResponse:
    course = await service.update_course(db, course_id, tenant.id, college.id, payload)
    return CourseResponse.model_validate(course)
