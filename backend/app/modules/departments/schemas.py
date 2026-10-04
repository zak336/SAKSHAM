"""Department Pydantic schemas."""

import uuid

from pydantic import BaseModel, Field, field_validator


class DepartmentCreateRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    code: str = Field(..., min_length=1, max_length=20)

    @field_validator("code")
    @classmethod
    def code_upper(cls, v: str) -> str:
        return v.upper()


class DepartmentUpdateRequest(BaseModel):
    name: str | None = Field(None, min_length=2, max_length=255)
    is_active: bool | None = None


class DepartmentResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    college_id: uuid.UUID
    name: str
    code: str
    is_active: bool

    model_config = {"from_attributes": True}
