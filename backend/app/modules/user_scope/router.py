"""Department scope assignment management for faculty and HOD users."""

import uuid
from typing import Annotated
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.dependencies import get_college, get_current_user, get_tenant, require_roles
from app.modules.colleges.models import College
from app.modules.tenants.models import Tenant
from app.modules.user_scope import service
from app.modules.user_scope.schemas import UserDepartmentCreateRequest, UserDepartmentResponse
from app.modules.users.models import User, UserRole

router = APIRouter(prefix="/users", tags=["user-scope"])
_manager_roles = require_roles(UserRole.admin, UserRole.super_admin)


@router.post("/{user_id}/departments", response_model=UserDepartmentResponse, status_code=status.HTTP_201_CREATED)
async def assign_department(user_id: uuid.UUID, payload: UserDepartmentCreateRequest, db: Annotated[AsyncSession, Depends(get_db)], tenant: Annotated[Tenant, Depends(get_tenant)], college: Annotated[College, Depends(get_college)], _: Annotated[User, Depends(_manager_roles)]) -> UserDepartmentResponse:
    item = await service.assign_department(db, tenant.id, college.id, user_id, payload)
    return UserDepartmentResponse.model_validate(item)


@router.get("/{user_id}/departments", response_model=list[UserDepartmentResponse])
async def list_assignments(user_id: uuid.UUID, db: Annotated[AsyncSession, Depends(get_db)], tenant: Annotated[Tenant, Depends(get_tenant)], college: Annotated[College, Depends(get_college)], current_user: Annotated[User, Depends(get_current_user)]) -> list[UserDepartmentResponse]:
    if current_user.role not in {UserRole.admin, UserRole.super_admin} and current_user.id != user_id:
        raise HTTPException(status_code=403, detail={"code": "PERMISSION_DENIED", "message": "You can only view your own department assignments."})
    items = await service.list_assignments(db, tenant.id, college.id, user_id)
    return [UserDepartmentResponse.model_validate(item) for item in items]


@router.delete("/{user_id}/departments/{department_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_assignment(user_id: uuid.UUID, department_id: uuid.UUID, db: Annotated[AsyncSession, Depends(get_db)], tenant: Annotated[Tenant, Depends(get_tenant)], college: Annotated[College, Depends(get_college)], _: Annotated[User, Depends(_manager_roles)]) -> None:
    await service.remove_assignment(db, tenant.id, college.id, user_id, department_id)
