import uuid
from datetime import date, datetime
from enum import Enum

from pydantic import BaseModel, Field


class AttendanceStatus(str, Enum):
    present = "present"
    absent = "absent"
    late = "late"
    excused = "excused"


class CourseEnrollmentCreateRequest(BaseModel):
    course_id: uuid.UUID
    student_id: uuid.UUID


class CourseEnrollmentResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    college_id: uuid.UUID
    course_id: uuid.UUID
    student_id: uuid.UUID
    created_at: datetime

    model_config = {"from_attributes": True}


class AttendanceSessionCreateRequest(BaseModel):
    course_id: uuid.UUID
    held_on: date
    period: int = Field(ge=1, le=20)


class AttendanceSessionResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    college_id: uuid.UUID
    course_id: uuid.UUID
    faculty_id: uuid.UUID
    held_on: date
    period: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AttendanceRecordInput(BaseModel):
    student_id: uuid.UUID
    status: AttendanceStatus


class BulkAttendanceRequest(BaseModel):
    records: list[AttendanceRecordInput]


class AttendanceRecordResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    college_id: uuid.UUID
    session_id: uuid.UUID
    student_id: uuid.UUID
    status: AttendanceStatus
    marked_at: datetime

    model_config = {"from_attributes": True}


class AttendanceSummaryResponse(BaseModel):
    student_id: uuid.UUID
    total_sessions: int
    present: int
    absent: int
    late: int
    excused: int
    percentage: float