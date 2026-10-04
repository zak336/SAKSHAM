"""Faculty repository."""

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.faculty.models import (
    FacultyAchievement,
    FacultyBookChapter,
    FacultyCourseAssignment,
    FacultyDevelopmentProgram,
    FacultyPatent,
    FacultyProfile,
    FacultyPublication,
)

async def get_by_id(
    db: AsyncSession,
    faculty_id: uuid.UUID,
    tenant_id: uuid.UUID,
    college_id: uuid.UUID,
) -> FacultyProfile | None:
    result = await db.execute(
        select(FacultyProfile).where(
            FacultyProfile.id == faculty_id,
            FacultyProfile.tenant_id == tenant_id,
            FacultyProfile.college_id == college_id,
        )
    )

    return result.scalar_one_or_none()


async def get_by_user_id(
    db: AsyncSession,
    user_id: uuid.UUID,
    tenant_id: uuid.UUID,
    college_id: uuid.UUID,
) -> FacultyProfile | None:
    result = await db.execute(
        select(FacultyProfile).where(
            FacultyProfile.user_id == user_id,
            FacultyProfile.tenant_id == tenant_id,
            FacultyProfile.college_id == college_id,
        )
    )

    return result.scalar_one_or_none()


async def list_all(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    college_id: uuid.UUID,
    department_id: uuid.UUID | None = None,
) -> list[FacultyProfile]:
    query = select(FacultyProfile).where(
        FacultyProfile.tenant_id == tenant_id,
        FacultyProfile.college_id == college_id,
    )

    if department_id is not None:
        query = query.where(
            FacultyProfile.department_id == department_id,
        )

    result = await db.execute(
        query.order_by(FacultyProfile.created_at)
    )

    return list(result.scalars().all())


async def create(
    db: AsyncSession,
    *,
    tenant_id: uuid.UUID,
    college_id: uuid.UUID,
    department_id: uuid.UUID,
    user_id: uuid.UUID,
    designation: str | None,
    qualification: str | None,
    joining_date,
    research_interests: str | None,
    bio: str | None,
) -> FacultyProfile:
    profile = FacultyProfile(
        tenant_id=tenant_id,
        college_id=college_id,
        department_id=department_id,
        user_id=user_id,
        designation=designation,
        qualification=qualification,
        joining_date=joining_date,
        research_interests=research_interests,
        bio=bio,
    )

    db.add(profile)
    await db.flush()
    await db.refresh(profile)

    return profile


async def update(
    db: AsyncSession,
    profile: FacultyProfile,
    **values,
) -> FacultyProfile:
    for key, value in values.items():
        if value is not None:
            setattr(profile, key, value)

    await db.flush()
    await db.refresh(profile)

    return profile

async def get_achievement_by_id(
    db: AsyncSession,
    *,
    achievement_id: uuid.UUID,
    tenant_id: uuid.UUID,
    college_id: uuid.UUID,
) -> FacultyAchievement | None:
    result = await db.execute(
        select(FacultyAchievement).where(
            FacultyAchievement.id == achievement_id,
            FacultyAchievement.tenant_id == tenant_id,
            FacultyAchievement.college_id == college_id,
        )
    )

    return result.scalar_one_or_none()


async def list_achievements(
    db: AsyncSession,
    *,
    faculty_id: uuid.UUID,
    tenant_id: uuid.UUID,
    college_id: uuid.UUID,
) -> list[FacultyAchievement]:
    result = await db.execute(
        select(FacultyAchievement)
        .where(
            FacultyAchievement.faculty_id == faculty_id,
            FacultyAchievement.tenant_id == tenant_id,
            FacultyAchievement.college_id == college_id,
        )
        .order_by(
            FacultyAchievement.achievement_date.desc().nullslast(),
            FacultyAchievement.created_at.desc(),
        )
    )

    return list(result.scalars().all())


async def create_achievement(
    db: AsyncSession,
    *,
    tenant_id: uuid.UUID,
    college_id: uuid.UUID,
    faculty_id: uuid.UUID,
    title: str,
    category: str,
    description: str | None,
    issuing_organization: str | None,
    achievement_date,
    reference_url: str | None,
) -> FacultyAchievement:
    achievement = FacultyAchievement(
        tenant_id=tenant_id,
        college_id=college_id,
        faculty_id=faculty_id,
        title=title,
        category=category,
        description=description,
        issuing_organization=issuing_organization,
        achievement_date=achievement_date,
        reference_url=reference_url,
    )

    db.add(achievement)
    await db.flush()
    await db.refresh(achievement)

    return achievement


async def update_achievement(
    db: AsyncSession,
    achievement: FacultyAchievement,
    **values,
) -> FacultyAchievement:
    for key, value in values.items():
        if value is not None:
            setattr(achievement, key, value)

    await db.flush()
    await db.refresh(achievement)

    return achievement


async def delete_achievement(
    db: AsyncSession,
    achievement: FacultyAchievement,
) -> None:
    await db.delete(achievement)
    await db.flush()


async def get_publication_by_id(
    db: AsyncSession,
    *,
    publication_id: uuid.UUID,
    tenant_id: uuid.UUID,
    college_id: uuid.UUID,
) -> FacultyPublication | None:
    result = await db.execute(
        select(FacultyPublication).where(
            FacultyPublication.id == publication_id,
            FacultyPublication.tenant_id == tenant_id,
            FacultyPublication.college_id == college_id,
        )
    )

    return result.scalar_one_or_none()


async def list_publications(
    db: AsyncSession,
    *,
    faculty_id: uuid.UUID,
    tenant_id: uuid.UUID,
    college_id: uuid.UUID,
) -> list[FacultyPublication]:
    result = await db.execute(
        select(FacultyPublication)
        .where(
            FacultyPublication.faculty_id == faculty_id,
            FacultyPublication.tenant_id == tenant_id,
            FacultyPublication.college_id == college_id,
        )
        .order_by(
            FacultyPublication.publication_date.desc().nullslast(),
            FacultyPublication.created_at.desc(),
        )
    )

    return list(result.scalars().all())


async def create_publication(
    db: AsyncSession,
    *,
    tenant_id: uuid.UUID,
    college_id: uuid.UUID,
    faculty_id: uuid.UUID,
    title: str,
    publication_type: str,
    journal_or_conference: str | None,
    publisher: str | None,
    publication_date,
    volume: str | None,
    issue: str | None,
    pages: str | None,
    doi: str | None,
    indexing: str | None,
    url: str | None,
    abstract: str | None,
) -> FacultyPublication:
    publication = FacultyPublication(
        tenant_id=tenant_id,
        college_id=college_id,
        faculty_id=faculty_id,
        title=title,
        publication_type=publication_type,
        journal_or_conference=journal_or_conference,
        publisher=publisher,
        publication_date=publication_date,
        volume=volume,
        issue=issue,
        pages=pages,
        doi=doi,
        indexing=indexing,
        url=url,
        abstract=abstract,
    )

    db.add(publication)
    await db.flush()
    await db.refresh(publication)

    return publication


async def update_publication(
    db: AsyncSession,
    publication: FacultyPublication,
    **values,
) -> FacultyPublication:
    for key, value in values.items():
        if value is not None:
            setattr(publication, key, value)

    await db.flush()
    await db.refresh(publication)

    return publication


async def delete_publication(
    db: AsyncSession,
    publication: FacultyPublication,
) -> None:
    await db.delete(publication)
    await db.flush()

async def get_patent_by_id(
    db: AsyncSession,
    *,
    patent_id: uuid.UUID,
    tenant_id: uuid.UUID,
    college_id: uuid.UUID,
) -> FacultyPatent | None:
    result = await db.execute(
        select(FacultyPatent).where(
            FacultyPatent.id == patent_id,
            FacultyPatent.tenant_id == tenant_id,
            FacultyPatent.college_id == college_id,
        )
    )

    return result.scalar_one_or_none()


async def list_patents(
    db: AsyncSession,
    *,
    faculty_id: uuid.UUID,
    tenant_id: uuid.UUID,
    college_id: uuid.UUID,
) -> list[FacultyPatent]:
    result = await db.execute(
        select(FacultyPatent)
        .where(
            FacultyPatent.faculty_id == faculty_id,
            FacultyPatent.tenant_id == tenant_id,
            FacultyPatent.college_id == college_id,
        )
        .order_by(
            FacultyPatent.filing_date.desc().nullslast(),
            FacultyPatent.created_at.desc(),
        )
    )

    return list(result.scalars().all())


async def create_patent(
    db: AsyncSession,
    *,
    tenant_id: uuid.UUID,
    college_id: uuid.UUID,
    faculty_id: uuid.UUID,
    title: str,
    patent_number: str | None,
    application_number: str | None,
    patent_type: str,
    status: str,
    filing_date,
    publication_date,
    grant_date,
    inventors: str | None,
    assignee: str | None,
    country: str | None,
    office: str | None,
    description: str | None,
    reference_url: str | None,
) -> FacultyPatent:
    patent = FacultyPatent(
        tenant_id=tenant_id,
        college_id=college_id,
        faculty_id=faculty_id,
        title=title,
        patent_number=patent_number,
        application_number=application_number,
        patent_type=patent_type,
        status=status,
        filing_date=filing_date,
        publication_date=publication_date,
        grant_date=grant_date,
        inventors=inventors,
        assignee=assignee,
        country=country,
        office=office,
        description=description,
        reference_url=reference_url,
    )

    db.add(patent)
    await db.flush()
    await db.refresh(patent)

    return patent


async def update_patent(
    db: AsyncSession,
    patent: FacultyPatent,
    **values,
) -> FacultyPatent:
    for key, value in values.items():
        if value is not None:
            setattr(patent, key, value)

    await db.flush()
    await db.refresh(patent)

    return patent


async def delete_patent(
    db: AsyncSession,
    patent: FacultyPatent,
) -> None:
    await db.delete(patent)
    await db.flush()

async def get_book_chapter_by_id(
    db: AsyncSession,
    *,
    chapter_id: uuid.UUID,
    tenant_id: uuid.UUID,
    college_id: uuid.UUID,
) -> FacultyBookChapter | None:
    result = await db.execute(
        select(FacultyBookChapter).where(
            FacultyBookChapter.id == chapter_id,
            FacultyBookChapter.tenant_id == tenant_id,
            FacultyBookChapter.college_id == college_id,
        )
    )

    return result.scalar_one_or_none()


async def list_book_chapters(
    db: AsyncSession,
    *,
    faculty_id: uuid.UUID,
    tenant_id: uuid.UUID,
    college_id: uuid.UUID,
) -> list[FacultyBookChapter]:
    result = await db.execute(
        select(FacultyBookChapter)
        .where(
            FacultyBookChapter.faculty_id == faculty_id,
            FacultyBookChapter.tenant_id == tenant_id,
            FacultyBookChapter.college_id == college_id,
        )
        .order_by(
            FacultyBookChapter.publication_date.desc().nullslast(),
            FacultyBookChapter.created_at.desc(),
        )
    )

    return list(result.scalars().all())


async def create_book_chapter(
    db: AsyncSession,
    *,
    tenant_id: uuid.UUID,
    college_id: uuid.UUID,
    faculty_id: uuid.UUID,
    chapter_title: str,
    book_title: str,
    publisher: str | None,
    publication_date,
    isbn: str | None,
    edition: str | None,
    chapter_number: str | None,
    pages: str | None,
    editors: str | None,
    doi: str | None,
    url: str | None,
    description: str | None,
) -> FacultyBookChapter:
    chapter = FacultyBookChapter(
        tenant_id=tenant_id,
        college_id=college_id,
        faculty_id=faculty_id,
        chapter_title=chapter_title,
        book_title=book_title,
        publisher=publisher,
        publication_date=publication_date,
        isbn=isbn,
        edition=edition,
        chapter_number=chapter_number,
        pages=pages,
        editors=editors,
        doi=doi,
        url=url,
        description=description,
    )

    db.add(chapter)
    await db.flush()
    await db.refresh(chapter)

    return chapter


async def update_book_chapter(
    db: AsyncSession,
    chapter: FacultyBookChapter,
    **values,
) -> FacultyBookChapter:
    for key, value in values.items():
        if value is not None:
            setattr(chapter, key, value)

    await db.flush()
    await db.refresh(chapter)

    return chapter


async def delete_book_chapter(
    db: AsyncSession,
    chapter: FacultyBookChapter,
) -> None:
    await db.delete(chapter)
    await db.flush()

async def get_course_assignment_by_id(
    db: AsyncSession,
    *,
    assignment_id: uuid.UUID,
    tenant_id: uuid.UUID,
    college_id: uuid.UUID,
) -> FacultyCourseAssignment | None:
    result = await db.execute(
        select(FacultyCourseAssignment).where(
            FacultyCourseAssignment.id == assignment_id,
            FacultyCourseAssignment.tenant_id == tenant_id,
            FacultyCourseAssignment.college_id == college_id,
        )
    )
    return result.scalar_one_or_none()


async def list_course_assignments(
    db: AsyncSession,
    *,
    faculty_id: uuid.UUID,
    tenant_id: uuid.UUID,
    college_id: uuid.UUID,
) -> list[FacultyCourseAssignment]:
    result = await db.execute(
        select(FacultyCourseAssignment)
        .where(
            FacultyCourseAssignment.faculty_id == faculty_id,
            FacultyCourseAssignment.tenant_id == tenant_id,
            FacultyCourseAssignment.college_id == college_id,
        )
        .order_by(
            FacultyCourseAssignment.academic_year.desc(),
            FacultyCourseAssignment.semester,
            FacultyCourseAssignment.created_at.desc(),
        )
    )
    return list(result.scalars().all())


async def create_course_assignment(
    db: AsyncSession,
    *,
    tenant_id: uuid.UUID,
    college_id: uuid.UUID,
    faculty_id: uuid.UUID,
    course_id: uuid.UUID,
    academic_year: str,
    semester: int,
    section: str | None,
    teaching_role: str,
    assigned_from,
    assigned_until,
) -> FacultyCourseAssignment:
    assignment = FacultyCourseAssignment(
        tenant_id=tenant_id,
        college_id=college_id,
        faculty_id=faculty_id,
        course_id=course_id,
        academic_year=academic_year,
        semester=semester,
        section=section,
        teaching_role=teaching_role,
        assigned_from=assigned_from,
        assigned_until=assigned_until,
    )
    db.add(assignment)
    await db.flush()
    await db.refresh(assignment)
    return assignment


async def update_course_assignment(
    db: AsyncSession,
    assignment: FacultyCourseAssignment,
    **values,
) -> FacultyCourseAssignment:
    for key, value in values.items():
        if value is not None:
            setattr(assignment, key, value)
    await db.flush()
    await db.refresh(assignment)
    return assignment


async def delete_course_assignment(
    db: AsyncSession,
    assignment: FacultyCourseAssignment,
) -> None:
    await db.delete(assignment)
    await db.flush()


async def get_fdp_by_id(
    db: AsyncSession,
    *,
    fdp_id: uuid.UUID,
    tenant_id: uuid.UUID,
    college_id: uuid.UUID,
) -> FacultyDevelopmentProgram | None:
    result = await db.execute(
        select(FacultyDevelopmentProgram).where(
            FacultyDevelopmentProgram.id == fdp_id,
            FacultyDevelopmentProgram.tenant_id == tenant_id,
            FacultyDevelopmentProgram.college_id == college_id,
        )
    )
    return result.scalar_one_or_none()


async def list_fdps(
    db: AsyncSession,
    *,
    faculty_id: uuid.UUID,
    tenant_id: uuid.UUID,
    college_id: uuid.UUID,
) -> list[FacultyDevelopmentProgram]:
    result = await db.execute(
        select(FacultyDevelopmentProgram)
        .where(
            FacultyDevelopmentProgram.faculty_id == faculty_id,
            FacultyDevelopmentProgram.tenant_id == tenant_id,
            FacultyDevelopmentProgram.college_id == college_id,
        )
        .order_by(
            FacultyDevelopmentProgram.start_date.desc().nullslast(),
            FacultyDevelopmentProgram.created_at.desc(),
        )
    )
    return list(result.scalars().all())


async def create_fdp(
    db: AsyncSession,
    *,
    tenant_id: uuid.UUID,
    college_id: uuid.UUID,
    faculty_id: uuid.UUID,
    title: str,
    organizer: str | None,
    program_type: str | None,
    mode: str | None,
    venue: str | None,
    start_date,
    end_date,
    duration_hours: float | None,
    certificate_number: str | None,
    certificate_url: str | None,
    description: str | None,
) -> FacultyDevelopmentProgram:
    fdp = FacultyDevelopmentProgram(
        tenant_id=tenant_id,
        college_id=college_id,
        faculty_id=faculty_id,
        title=title,
        organizer=organizer,
        program_type=program_type,
        mode=mode,
        venue=venue,
        start_date=start_date,
        end_date=end_date,
        duration_hours=duration_hours,
        certificate_number=certificate_number,
        certificate_url=certificate_url,
        description=description,
    )
    db.add(fdp)
    await db.flush()
    await db.refresh(fdp)
    return fdp


async def update_fdp(
    db: AsyncSession,
    fdp: FacultyDevelopmentProgram,
    **values,
) -> FacultyDevelopmentProgram:
    for key, value in values.items():
        if value is not None:
            setattr(fdp, key, value)
    await db.flush()
    await db.refresh(fdp)
    return fdp


async def delete_fdp(
    db: AsyncSession,
    fdp: FacultyDevelopmentProgram,
) -> None:
    await db.delete(fdp)
    await db.flush()
