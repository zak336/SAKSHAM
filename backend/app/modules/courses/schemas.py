"""Course Pydantic schemas."""

import uuid

from pydantic import BaseModel, Field, field_validator


class CourseCreateRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    code: str = Field(..., min_length=1, max_length=20)
    department_id: uuid.UUID
    semester: int = Field(..., ge=1, le=12)
    credits: int = Field(3, ge=1, le=10)
    faculty_id: uuid.UUID | None = None

    @field_validator("code")
    @classmethod
    def code_upper(cls, v: str) -> str:
        return v.upper()


class CourseUpdateRequest(BaseModel):
    name: str | None = Field(None, min_length=2, max_length=255)
    faculty_id: uuid.UUID | None = None
    credits: int | None = Field(None, ge=1, le=10)
    is_active: bool | None = None


class CourseResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    college_id: uuid.UUID
    department_id: uuid.UUID
    faculty_id: uuid.UUID | None
    name: str
    code: str
    semester: int
    credits: int
    is_active: bool

    model_config = {"from_attributes": True}
