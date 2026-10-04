"""Departments router."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_college, get_department_scope, get_tenant, require_department_access, require_module, require_roles
from app.modules.colleges.models import College
from app.modules.departments import service
from app.modules.departments.schemas import DepartmentCreateRequest, DepartmentResponse, DepartmentUpdateRequest
from app.modules.tenants.models import Tenant
from app.modules.users.models import User, UserRole

_module_access = require_module("departments")
router = APIRouter(prefix="/departments", tags=["departments"], dependencies=[Depends(_module_access)])
_admin_roles = require_roles(UserRole.admin, UserRole.super_admin)


@router.post("", response_model=DepartmentResponse, status_code=status.HTTP_201_CREATED)
async def create_department(
    payload: DepartmentCreateRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    tenant: Annotated[Tenant, Depends(get_tenant)],
    college: Annotated[College, Depends(get_college)],
    _: Annotated[User, Depends(_admin_roles)],
) -> DepartmentResponse:
    dept = await service.create_department(db, tenant.id, college.id, payload)
    return DepartmentResponse.model_validate(dept)


@router.get("", response_model=list[DepartmentResponse])
async def list_departments(
    db: Annotated[AsyncSession, Depends(get_db)],
    tenant: Annotated[Tenant, Depends(get_tenant)],
    college: Annotated[College, Depends(get_college)],
    _: Annotated[User, Depends(require_roles(UserRole.admin, UserRole.super_admin, UserRole.faculty, UserRole.hod, UserRole.student))],
    department_scope: Annotated[set[uuid.UUID] | None, Depends(get_department_scope)],
) -> list[DepartmentResponse]:
    depts = await service.list_departments(db, tenant.id, college.id, department_ids=department_scope)
    return [DepartmentResponse.model_validate(d) for d in depts]


@router.get("/{dept_id}", response_model=DepartmentResponse)
async def get_department(
    dept_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    tenant: Annotated[Tenant, Depends(get_tenant)],
    college: Annotated[College, Depends(get_college)],
    _: Annotated[User, Depends(require_roles(UserRole.admin, UserRole.super_admin, UserRole.faculty, UserRole.hod, UserRole.student))],
    __: Annotated[User, Depends(require_department_access)],
) -> DepartmentResponse:
    dept = await service.get_department(db, dept_id, tenant.id, college.id)
    return DepartmentResponse.model_validate(dept)


@router.patch("/{dept_id}", response_model=DepartmentResponse)
async def update_department(
    dept_id: uuid.UUID,
    payload: DepartmentUpdateRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    tenant: Annotated[Tenant, Depends(get_tenant)],
    college: Annotated[College, Depends(get_college)],
    _: Annotated[User, Depends(_admin_roles)],
) -> DepartmentResponse:
    dept = await service.update_department(db, dept_id, tenant.id, college.id, payload)
    return DepartmentResponse.model_validate(dept)
