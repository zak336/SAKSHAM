"""Students router."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_college, get_current_user, get_department_scope, get_tenant, require_department_access, require_module, require_roles
from app.modules.colleges.models import College
from app.modules.students import service
from app.modules.students.schemas import StudentCreateRequest, StudentDetailResponse, StudentResponse, StudentUpdateRequest
from app.modules.tenants.models import Tenant
from app.modules.users.models import User, UserRole

_module_access = require_module("students")
router = APIRouter(prefix="/students", tags=["students"], dependencies=[Depends(_module_access)])
_admin_roles = require_roles(UserRole.admin, UserRole.super_admin)
_staff_roles = require_roles(UserRole.admin, UserRole.super_admin, UserRole.faculty, UserRole.hod)


@router.post("", response_model=StudentResponse, status_code=status.HTTP_201_CREATED)
async def create_student(
    payload: StudentCreateRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    tenant: Annotated[Tenant, Depends(get_tenant)],
    college: Annotated[College, Depends(get_college)],
    _: Annotated[User, Depends(_admin_roles)],
) -> StudentResponse:
    student = await service.create_student(db, tenant.id, college.id, payload)
    return StudentResponse.model_validate(student)


@router.get("", response_model=list[StudentResponse])
async def list_students(
    db: Annotated[AsyncSession, Depends(get_db)],
    tenant: Annotated[Tenant, Depends(get_tenant)],
    college: Annotated[College, Depends(get_college)],
    _: Annotated[User, Depends(_staff_roles)],
    department_scope: Annotated[set[uuid.UUID] | None, Depends(get_department_scope)],
    department_id: uuid.UUID | None = Query(None),
    semester: int | None = Query(None),
    batch_year: int | None = Query(None),
) -> list[StudentResponse]:
    students = await service.list_students(
        db,
        tenant.id,
        college.id,
        department_id=department_id,
        semester=semester,
        batch_year=batch_year,
        department_ids=department_scope,
    )
    return [StudentResponse.model_validate(s) for s in students]


@router.get("/me", response_model=StudentDetailResponse)
async def get_my_student_profile(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    tenant: Annotated[Tenant, Depends(get_tenant)],
    college: Annotated[College, Depends(get_college)],
) -> StudentDetailResponse:
    from app.core.exceptions import NotFoundError
    from app.modules.students.repository import get_by_user_id

    student = await get_by_user_id(db, current_user.id, tenant.id, college.id)
    if student is None:
        raise NotFoundError("No student profile found for this user in this college.")
    return await service.get_student_detail(db, student.id, tenant.id, college.id)


@router.get("/{student_id}", response_model=StudentDetailResponse)
async def get_student(
    student_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    tenant: Annotated[Tenant, Depends(get_tenant)],
    college: Annotated[College, Depends(get_college)],
    current_user: Annotated[User, Depends(_staff_roles)],
) -> StudentDetailResponse:
    result = await service.get_student_detail(db, student_id, tenant.id, college.id)
    if current_user.role in {UserRole.faculty, UserRole.hod}:
        from app.modules.user_scope.repository import get_assignment
        if await get_assignment(db, tenant.id, current_user.id, college.id, result.department_id) is None:
            raise HTTPException(status_code=403, detail={"code": "DEPARTMENT_ACCESS_DENIED", "message": "You do not have access to this student."})
    return result


@router.patch("/{student_id}", response_model=StudentResponse)
async def update_student(
    student_id: uuid.UUID,
    payload: StudentUpdateRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    tenant: Annotated[Tenant, Depends(get_tenant)],
    college: Annotated[College, Depends(get_college)],
    _: Annotated[User, Depends(_admin_roles)],
) -> StudentResponse:
    student = await service.update_student(db, student_id, tenant.id, college.id, payload)
    return StudentResponse.model_validate(student)
