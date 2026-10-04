"""Faculty API schemas."""

import uuid
from datetime import date, datetime

from pydantic import BaseModel, Field


class FacultyCreateRequest(BaseModel):
    user_id: uuid.UUID
    department_id: uuid.UUID
    designation: str | None = Field(None, max_length=100)
    qualification: str | None = Field(None, max_length=255)
    joining_date: date | None = None
    research_interests: str | None = None
    bio: str | None = None

class FacultyUpdateRequest(BaseModel):
    department_id: uuid.UUID | None = None
    designation: str | None = Field(None, max_length=100)
    qualification: str | None = Field(None, max_length=255)
    joining_date: date | None = None
    research_interests: str | None = None
    bio: str | None = None

class FacultyProfileResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    college_id: uuid.UUID
    department_id: uuid.UUID
    user_id: uuid.UUID

    designation: str | None
    qualification: str | None
    joining_date: date | None
    research_interests: str | None
    bio: str | None

    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

class FacultyAchievementCreateRequest(BaseModel):
    title: str = Field(..., min_length=2, max_length=255)
    category: str = Field(..., min_length=2, max_length=50)
    description: str | None = None
    issuing_organization: str | None = Field(
        None,
        max_length=255,
    )
    achievement_date: date | None = None
    reference_url: str | None = Field(
        None,
        max_length=2048,
    )

class FacultyAchievementUpdateRequest(BaseModel):
    title: str | None = Field(
        None,
        min_length=2,
        max_length=255,
    )
    category: str | None = Field(
        None,
        min_length=2,
        max_length=50,
    )
    description: str | None = None
    issuing_organization: str | None = Field(
        None,
        max_length=255,
    )
    achievement_date: date | None = None
    reference_url: str | None = Field(
        None,
        max_length=2048,
    )

class FacultyAchievementResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    college_id: uuid.UUID
    faculty_id: uuid.UUID
    title: str
    category: str
    description: str | None
    issuing_organization: str | None
    achievement_date: date | None
    reference_url: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

class FacultyPublicationCreateRequest(BaseModel):
    title: str = Field(
        ...,
        min_length=2,
        max_length=500,
    )

    publication_type: str = Field(
        ...,
        min_length=2,
        max_length=50,
    )

    journal_or_conference: str | None = Field(
        None,
        max_length=500,
    )

    publisher: str | None = Field(
        None,
        max_length=255,
    )

    publication_date: date | None = None

    volume: str | None = Field(
        None,
        max_length=50,
    )

    issue: str | None = Field(
        None,
        max_length=50,
    )

    pages: str | None = Field(
        None,
        max_length=100,
    )

    doi: str | None = Field(
        None,
        max_length=255,
    )

    indexing: str | None = Field(
        None,
        max_length=255,
    )

    url: str | None = Field(
        None,
        max_length=2048,
    )

    abstract: str | None = None

class FacultyPublicationUpdateRequest(BaseModel):
    title: str | None = Field(
        None,
        min_length=2,
        max_length=500,
    )

    publication_type: str | None = Field(
        None,
        min_length=2,
        max_length=50,
    )

    journal_or_conference: str | None = Field(
        None,
        max_length=500,
    )

    publisher: str | None = Field(
        None,
        max_length=255,
    )

    publication_date: date | None = None

    volume: str | None = Field(
        None,
        max_length=50,
    )

    issue: str | None = Field(
        None,
        max_length=50,
    )

    pages: str | None = Field(
        None,
        max_length=100,
    )

    doi: str | None = Field(
        None,
        max_length=255,
    )

    indexing: str | None = Field(
        None,
        max_length=255,
    )

    url: str | None = Field(
        None,
        max_length=2048,
    )

    abstract: str | None = None

class FacultyPublicationResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    college_id: uuid.UUID
    faculty_id: uuid.UUID
    title: str
    publication_type: str
    journal_or_conference: str | None
    publisher: str | None
    publication_date: date | None
    volume: str | None
    issue: str | None
    pages: str | None
    doi: str | None
    indexing: str | None
    url: str | None
    abstract: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

class FacultyPatentCreateRequest(BaseModel):
    title: str = Field(..., min_length=2, max_length=500)
    patent_number: str | None = Field(None, max_length=255)
    application_number: str | None = Field(None, max_length=255)
    patent_type: str = Field(..., min_length=2, max_length=50)
    status: str = Field(..., min_length=2, max_length=50)
    filing_date: date | None = None
    publication_date: date | None = None
    grant_date: date | None = None
    inventors: str | None = None
    assignee: str | None = Field(None, max_length=500)
    country: str | None = Field(None, max_length=100)
    office: str | None = Field(None, max_length=255)
    description: str | None = None
    reference_url: str | None = Field(None, max_length=2048)

class FacultyPatentUpdateRequest(BaseModel):
    title: str | None = Field(None, min_length=2, max_length=500)
    patent_number: str | None = Field(None, max_length=255)
    application_number: str | None = Field(None, max_length=255)
    patent_type: str | None = Field(None, min_length=2, max_length=50)
    status: str | None = Field(None, min_length=2, max_length=50)
    filing_date: date | None = None
    publication_date: date | None = None
    grant_date: date | None = None
    inventors: str | None = None
    assignee: str | None = Field(None, max_length=500)
    country: str | None = Field(None, max_length=100)
    office: str | None = Field(None, max_length=255)
    description: str | None = None
    reference_url: str | None = Field(None, max_length=2048)

class FacultyPatentResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    college_id: uuid.UUID
    faculty_id: uuid.UUID
    title: str
    patent_number: str | None
    application_number: str | None
    patent_type: str
    status: str
    filing_date: date | None
    publication_date: date | None
    grant_date: date | None
    inventors: str | None
    assignee: str | None
    country: str | None
    office: str | None
    description: str | None
    reference_url: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

class FacultyBookChapterCreateRequest(BaseModel):
    chapter_title: str = Field(
        ...,
        min_length=2,
        max_length=500,
    )
    book_title: str = Field(
        ...,
        min_length=2,
        max_length=500,
    )
    publisher: str | None = Field(
        None,
        max_length=500,
    )
    publication_date: date | None = None
    isbn: str | None = Field(
        None,
        max_length=100,
    )
    edition: str | None = Field(
        None,
        max_length=100,
    )
    chapter_number: str | None = Field(
        None,
        max_length=50,
    )
    pages: str | None = Field(
        None,
        max_length=100,
    )
    editors: str | None = None
    doi: str | None = Field(
        None,
        max_length=255,
    )
    url: str | None = Field(
        None,
        max_length=2048,
    )
    description: str | None = None

class FacultyBookChapterUpdateRequest(BaseModel):
    chapter_title: str | None = Field(
        None,
        min_length=2,
        max_length=500,
    )
    book_title: str | None = Field(
        None,
        min_length=2,
        max_length=500,
    )
    publisher: str | None = Field(
        None,
        max_length=500,
    )
    publication_date: date | None = None
    isbn: str | None = Field(
        None,
        max_length=100,
    )
    edition: str | None = Field(
        None,
        max_length=100,
    )
    chapter_number: str | None = Field(
        None,
        max_length=50,
    )
    pages: str | None = Field(
        None,
        max_length=100,
    )
    editors: str | None = None
    doi: str | None = Field(
        None,
        max_length=255,
    )
    url: str | None = Field(
        None,
        max_length=2048,
    )
    description: str | None = None

class FacultyBookChapterResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    college_id: uuid.UUID
    faculty_id: uuid.UUID
    chapter_title: str
    book_title: str
    publisher: str | None
    publication_date: date | None
    isbn: str | None
    edition: str | None
    chapter_number: str | None
    pages: str | None
    editors: str | None
    doi: str | None
    url: str | None
    description: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

class FacultyCourseAssignmentCreateRequest(BaseModel):
    course_id: uuid.UUID
    academic_year: str = Field(..., min_length=4, max_length=20)
    semester: int = Field(..., ge=1, le=20)
    section: str | None = Field(None, max_length=50)
    teaching_role: str = Field("primary", min_length=2, max_length=50)
    assigned_from: date | None = None
    assigned_until: date | None = None

class FacultyCourseAssignmentUpdateRequest(BaseModel):
    course_id: uuid.UUID | None = None
    academic_year: str | None = Field(None, min_length=4, max_length=20)
    semester: int | None = Field(None, ge=1, le=20)
    section: str | None = Field(None, max_length=50)
    teaching_role: str | None = Field(None, min_length=2, max_length=50)
    assigned_from: date | None = None
    assigned_until: date | None = None

class FacultyCourseAssignmentResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    college_id: uuid.UUID
    faculty_id: uuid.UUID
    course_id: uuid.UUID
    academic_year: str
    semester: int
    section: str | None
    teaching_role: str
    assigned_from: date | None
    assigned_until: date | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

class FacultyDevelopmentProgramCreateRequest(BaseModel):
    title: str = Field(..., min_length=2, max_length=500)
    organizer: str | None = Field(None, max_length=500)
    program_type: str | None = Field(None, max_length=100)
    mode: str | None = Field(None, max_length=50)
    venue: str | None = Field(None, max_length=500)
    start_date: date | None = None
    end_date: date | None = None
    duration_hours: float | None = Field(None, ge=0)
    certificate_number: str | None = Field(None, max_length=255)
    certificate_url: str | None = Field(None, max_length=2048)
    description: str | None = None

class FacultyDevelopmentProgramUpdateRequest(BaseModel):
    title: str | None = Field(None, min_length=2, max_length=500)
    organizer: str | None = Field(None, max_length=500)
    program_type: str | None = Field(None, max_length=100)
    mode: str | None = Field(None, max_length=50)
    venue: str | None = Field(None, max_length=500)
    start_date: date | None = None
    end_date: date | None = None
    duration_hours: float | None = Field(None, ge=0)
    certificate_number: str | None = Field(None, max_length=255)
    certificate_url: str | None = Field(None, max_length=2048)
    description: str | None = None

class FacultyDevelopmentProgramResponse(BaseModel):
    id: uuid.UUID
    tenant_id: uuid.UUID
    college_id: uuid.UUID
    faculty_id: uuid.UUID
    title: str
    organizer: str | None
    program_type: str | None
    mode: str | None
    venue: str | None
    start_date: date | None
    end_date: date | None
    duration_hours: float | None
    certificate_number: str | None
    certificate_url: str | None
    description: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

