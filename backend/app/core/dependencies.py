"""Shared FastAPI dependencies used across all modules."""

from collections.abc import Callable
import uuid
from typing import Annotated

from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import decode_token
from app.modules.colleges.models import College
from app.modules.tenants.models import Tenant
from app.modules.users.models import User, UserRole


bearer_scheme = HTTPBearer()


async def get_current_user(
    credentials: Annotated[
        HTTPAuthorizationCredentials,
        Depends(bearer_scheme),
    ],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    """
    Decode the Bearer access token and return the authenticated user.

    Raises 401 if the token is missing, invalid, expired, or the user
    no longer exists/is inactive.
    """
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={
            "code": "UNAUTHENTICATED",
            "message": "Invalid or expired token",
        },
        headers={"WWW-Authenticate": "Bearer"},
    )

    token = credentials.credentials

    try:
        payload = decode_token(token)
    except JWTError as err:
        raise credentials_error from err

    if payload.get("type") != "access":
        raise credentials_error

    user_id: str | None = payload.get("sub")

    if user_id is None:
        raise credentials_error

    result = await db.execute(
        select(User).where(
            User.id == user_id,
            User.is_active.is_(True),
        )
    )

    user = result.scalar_one_or_none()

    if user is None:
        raise credentials_error

    return user


async def get_tenant(
    x_tenant_id: Annotated[str, Header(alias="X-Tenant-ID")],
    current_user: Annotated[User, Depends(get_current_user)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> Tenant:
    """
    Resolve the tenant from X-Tenant-ID.

    Normal tenant users can only access their own tenant.

    Super admins are platform-level users and may explicitly select
    another tenant using X-Tenant-ID.
    """

    result = await db.execute(
        select(Tenant).where(
            Tenant.slug == x_tenant_id,
            Tenant.is_active.is_(True),
        )
    )

    tenant = result.scalar_one_or_none()

    if tenant is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "TENANT_NOT_FOUND",
                "message": f"Tenant '{x_tenant_id}' not found",
            },
        )

    # Super admins operate at the platform level and may access
    # multiple tenants explicitly.
    if current_user.role != UserRole.super_admin:
        if tenant.id != current_user.tenant_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "code": "TENANT_ACCESS_DENIED",
                    "message": "You do not have access to this tenant.",
                },
            )

    return tenant


def require_roles(*roles: UserRole) -> Callable:
    """
    FastAPI dependency factory that enforces role-based access control.

    Usage:
        Depends(require_roles(UserRole.admin, UserRole.super_admin))
    """

    async def _check(
        current_user: Annotated[User, Depends(get_current_user)],
    ) -> User:
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "code": "PERMISSION_DENIED",
                    "message": "You do not have permission to perform this action.",
                },
            )

        return current_user

    return _check


async def get_college(
    x_college_id: Annotated[str, Header(alias="X-College-ID")],
    current_user: Annotated[User, Depends(get_current_user)],
    tenant: Annotated[Tenant, Depends(get_tenant)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> College:
    """Resolve the selected college and enforce the user's college scope."""
    try:
        college_id = uuid.UUID(x_college_id)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "code": "INVALID_COLLEGE_ID",
                "message": "X-College-ID must be a valid UUID.",
            },
        ) from exc

    result = await db.execute(
        select(College).where(
            College.id == college_id,
            College.tenant_id == tenant.id,
            College.is_active.is_(True),
        )
    )
    college = result.scalar_one_or_none()

    if college is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "COLLEGE_NOT_FOUND",
                "message": "College not found in this tenant.",
            },
        )

    if current_user.role != UserRole.super_admin and current_user.college_id != college.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "COLLEGE_ACCESS_DENIED",
                "message": "You do not have access to this college.",
            },
        )

    return college

async def get_department_scope(
    current_user: Annotated[User, Depends(get_current_user)],
    tenant: Annotated[Tenant, Depends(get_tenant)],
    college: Annotated[College, Depends(get_college)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> set[uuid.UUID] | None:
    """Return allowed department IDs for scoped roles.
    None means unrestricted within the tenant.
    Faculty:
        Their primary faculty department is always included.
        Additional departments may come from user_departments.
    HOD:
        Departments come from explicit user_departments assignments.
    Student:
        Only their own student department.
    """
    if current_user.role in {
        UserRole.super_admin,
        UserRole.admin,
    }:
        return None

    if current_user.role == UserRole.faculty:
        from app.modules.faculty.models import FacultyProfile
        from app.modules.user_scope.repository import department_ids

        allowed_ids = await department_ids(
            db,
            tenant.id,
            college.id,
            current_user.id,
        )

        result = await db.execute(
            select(FacultyProfile.department_id).where(
                FacultyProfile.tenant_id == tenant.id,
                FacultyProfile.college_id == college.id,
                FacultyProfile.user_id == current_user.id,
            )
        )

        primary_department_id = result.scalar_one_or_none()

        if primary_department_id is not None:
            allowed_ids.add(primary_department_id)

        return allowed_ids

    if current_user.role == UserRole.hod:
        from app.modules.user_scope.repository import department_ids

        return await department_ids(
            db,
            tenant.id,
            college.id,
            current_user.id,
        )

    if current_user.role == UserRole.student:
        from app.modules.students.models import Student

        result = await db.execute(
            select(Student.department_id).where(
                Student.tenant_id == tenant.id,
                Student.college_id == college.id,
                Student.user_id == current_user.id,
            )
        )

        department_id = result.scalar_one_or_none()

        return (
            {department_id}
            if department_id is not None
            else set()
        )

    return set()


async def require_department_access(
    department_id: uuid.UUID,
    current_user: Annotated[User, Depends(get_current_user)],
    tenant: Annotated[Tenant, Depends(get_tenant)],
    college: Annotated[College, Depends(get_college)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    """Verify that the current user may access a specific department."""

    # Platform and tenant administrators have unrestricted access
    # within the resolved tenant context.
    if current_user.role in {UserRole.super_admin, UserRole.admin}:
        return current_user

    # Faculty and HOD users must have an explicit department assignment.
    if current_user.role == UserRole.faculty:
        from app.modules.faculty.models import FacultyProfile
        from app.modules.user_scope.repository import get_assignment

        # Primary faculty department always grants access.
        result = await db.execute(
            select(FacultyProfile.department_id).where(
                FacultyProfile.tenant_id == tenant.id,
                FacultyProfile.college_id == college.id,
                FacultyProfile.user_id == current_user.id,
            )
        )

        primary_department_id = result.scalar_one_or_none()

        if primary_department_id == department_id:
            return current_user

        # Additional department assignments grant access too.
        assignment = await get_assignment(
            db,
            tenant.id,
            current_user.id,
            college.id,
            department_id,
        )

        if assignment is not None:
            return current_user

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "DEPARTMENT_ACCESS_DENIED",
                "message": "You do not have access to this department.",
            },
        )

    if current_user.role == UserRole.hod:
        from app.modules.user_scope.repository import get_assignment

        assignment = await get_assignment(
            db,
            tenant.id,
            current_user.id,
            college.id,
            department_id,
        )

        if assignment is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "code": "DEPARTMENT_ACCESS_DENIED",
                    "message": "You do not have access to this department.",
                },
            )

    return current_user

    # Students may only access their own department.
    if current_user.role == UserRole.student:
        from app.modules.students.models import Student

        result = await db.execute(
            select(Student.department_id).where(
                Student.tenant_id == tenant.id,
                Student.college_id == college.id,
                Student.user_id == current_user.id,
            )
        )

        student_department_id = result.scalar_one_or_none()

        if student_department_id != department_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "code": "DEPARTMENT_ACCESS_DENIED",
                    "message": "You do not have access to this department.",
                },
            )

        return current_user

    # Other roles do not receive department access by default.
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail={
            "code": "DEPARTMENT_ACCESS_DENIED",
            "message": "You do not have access to this department.",
        },
    )


def require_module(module_key: str) -> Callable:
    """FastAPI dependency factory for tenant module entitlements."""
    async def _check(
        tenant: Annotated[Tenant, Depends(get_tenant)],
        db: Annotated[AsyncSession, Depends(get_db)],
    ) -> None:
        from app.modules.entitlements.service import is_module_enabled
        if not await is_module_enabled(db, tenant.id, module_key):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "code": "MODULE_NOT_ENABLED",
                    "message": f"The '{module_key}' module is not enabled for this tenant.",
                },
            )
    return _check
