"""College API schemas."""

import uuid

from pydantic import BaseModel, Field, field_validator


class CollegeCreateRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    code: str = Field(..., min_length=1, max_length=30)
    slug: str = Field(..., min_length=2, max_length=100, pattern=r"^[a-z0-9\-]+$")

    @field_validator("code")
    @classmethod
    def code_upper(cls, value: str) -> str:
        return value.upper().strip()

    @field_validator("slug")
    @classmethod
    def slug_lowercase(cls, value: str) -> str:
        return value.lower().strip()


class CollegeUpdateRequest(BaseModel):
    name: str | None = Field(None, min_length=2, max_length=255)
    code: str | None = Field(None, min_length=1, max_length=30)
    is_active: bool | None = None

    @field_validator("code")
    @classmethod
    def code_upper(cls, value: str | None) -> str | None:
        return value.upper().strip() if value is not None else None


class CollegeResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    name: str
    code: str
    slug: str
    is_active: bool

    model_config = {"from_attributes": True}
