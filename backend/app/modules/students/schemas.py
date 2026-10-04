"""Student Pydantic schemas."""

import uuid

from pydantic import BaseModel, Field


class StudentCreateRequest(BaseModel):
    """Create a student profile linked to an existing user account."""

    user_id: uuid.UUID
    department_id: uuid.UUID
    roll_number: str = Field(..., min_length=1, max_length=50)
    batch_year: int = Field(..., ge=2000, le=2100)
    current_semester: int = Field(..., ge=1, le=12)


class StudentUpdateRequest(BaseModel):
    department_id: uuid.UUID | None = None
    current_semester: int | None = Field(None, ge=1, le=12)
    roll_number: str | None = Field(None, min_length=1, max_length=50)


class StudentResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    college_id: uuid.UUID
    user_id: uuid.UUID
    department_id: uuid.UUID
    roll_number: str
    batch_year: int
    current_semester: int

    model_config = {"from_attributes": True}


class StudentDetailResponse(StudentResponse):
    """Extended response with user and department names."""

    student_name: str
    email: str
    department_name: str
    department_code: str
