"""User Pydantic schemas."""

import uuid

from pydantic import BaseModel, EmailStr, Field

from app.modules.users.models import UserRole


class UserResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    college_id: uuid.UUID | None
    name: str
    email: EmailStr
    phone: str | None
    role: UserRole
    is_active: bool

    model_config = {"from_attributes": True}


class UserCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    email: EmailStr
    password: str = Field(..., min_length=8)
    phone: str | None = Field(None, max_length=20)
    role: UserRole


class UserUpdateRequest(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    phone: str | None = Field(None, max_length=20)


class AdminUserUpdateRequest(BaseModel):
    """Admin-level update: can also change role and active status."""

    name: str | None = Field(None, min_length=1, max_length=255)
    phone: str | None = Field(None, max_length=20)
    role: UserRole | None = None
    is_active: bool | None = None
