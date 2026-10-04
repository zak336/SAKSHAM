"""MOOC completion API schemas."""

import uuid
from datetime import date, datetime

from pydantic import BaseModel, Field


class MoocCompletionCreateRequest(BaseModel):
    user_id: uuid.UUID | None = None
    course_title: str = Field(..., min_length=2, max_length=500)
    provider: str | None = Field(None, max_length=255)
    platform: str | None = Field(None, max_length=255)
    course_identifier: str | None = Field(None, max_length=255)
    duration_hours: float | None = Field(None, ge=0)
    enrolled_on: date | None = None
    completed_on: date | None = None
    certificate_id: str | None = Field(None, max_length=255)
    certificate_url: str | None = Field(None, max_length=2048)
    score: float | None = Field(None, ge=0, le=100)
    status: str = Field("completed", min_length=2, max_length=50)
    description: str | None = None


class MoocCompletionUpdateRequest(BaseModel):
    course_title: str | None = Field(None, min_length=2, max_length=500)
    provider: str | None = Field(None, max_length=255)
    platform: str | None = Field(None, max_length=255)
    course_identifier: str | None = Field(None, max_length=255)
    duration_hours: float | None = Field(None, ge=0)
    enrolled_on: date | None = None
    completed_on: date | None = None
    certificate_id: str | None = Field(None, max_length=255)
    certificate_url: str | None = Field(None, max_length=2048)
    score: float | None = Field(None, ge=0, le=100)
    status: str | None = Field(None, min_length=2, max_length=50)
    description: str | None = None


class MoocCompletionResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    college_id: uuid.UUID
    user_id: uuid.UUID
    course_title: str
    provider: str | None
    platform: str | None
    course_identifier: str | None
    duration_hours: float | None
    enrolled_on: date | None
    completed_on: date | None
    certificate_id: str | None
    certificate_url: str | None
    score: float | None
    status: str
    description: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
