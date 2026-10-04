"""Faculty business logic and authorization."""

import uuid

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.colleges.models import College
from app.modules.departments.models import Department
from app.modules.faculty import repository
from app.modules.users.models import User, UserRole
from app.modules.faculty.models import (
    FacultyAchievement,
    FacultyBookChapter,
    FacultyCourseAssignment,
    FacultyDevelopmentProgram,
    FacultyPatent,
    FacultyProfile,
    FacultyPublication,
)

from app.modules.faculty.schemas import (
    FacultyAchievementCreateRequest,
    FacultyAchievementUpdateRequest,
    FacultyBookChapterCreateRequest,
    FacultyBookChapterUpdateRequest,
    FacultyCourseAssignmentCreateRequest,
    FacultyCourseAssignmentUpdateRequest,
    FacultyDevelopmentProgramCreateRequest,
    FacultyDevelopmentProgramUpdateRequest,
    FacultyCreateRequest,
    FacultyPatentCreateRequest,
    FacultyPatentUpdateRequest,
    FacultyPublicationCreateRequest,
    FacultyPublicationUpdateRequest,
    FacultyUpdateRequest,
)


def _forbidden(code: str, message: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail={
            "code": code,
            "message": message,
        },
    )


async def _validate_department(
    db: AsyncSession,
    *,
    tenant_id: uuid.UUID,
    college_id: uuid.UUID,
    department_id: uuid.UUID,
) -> Department:
    result = await db.execute(
        select(Department).where(
            Department.id == department_id,
            Department.tenant_id == tenant_id,
            Department.college_id == college_id,
            Department.is_active.is_(True),
        )
    )

    department = result.scalar_one_or_none()

    if department is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "DEPARTMENT_NOT_FOUND",
                "message": "Department not found in this college.",
            },
        )

    return department


async def create_faculty(
    db: AsyncSession,
    *,
    current_user: User,
    tenant_id: uuid.UUID,
    college_id: uuid.UUID,
    payload: FacultyCreateRequest,
) -> FacultyProfile:

    if current_user.role not in {
        UserRole.super_admin,
        UserRole.admin,
        UserRole.hod,
    }:
        raise _forbidden(
            "FACULTY_MANAGEMENT_DENIED",
            "You do not have permission to create faculty profiles.",
        )

    await _validate_department(
        db,
        tenant_id=tenant_id,
        college_id=college_id,
        department_id=payload.department_id,
    )

    user_result = await db.execute(
        select(User).where(
            User.id == payload.user_id,
            User.tenant_id == tenant_id,
            User.college_id == college_id,
            User.is_active.is_(True),
        )
    )

    user = user_result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "USER_NOT_FOUND",
                "message": "User not found in this college.",
            },
        )

    if user.role != UserRole.faculty:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "code": "USER_NOT_FACULTY",
                "message": "The selected user does not have the faculty role.",
            },
        )

    existing = await repository.get_by_user_id(
        db,
        payload.user_id,
        tenant_id,
        college_id,
    )

    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "code": "FACULTY_PROFILE_EXISTS",
                "message": "This faculty user already has a profile.",
            },
        )

    if current_user.role == UserRole.hod:
        from app.modules.user_scope.repository import get_assignment

        assignment = await get_assignment(
            db,
            tenant_id,
            current_user.id,
            college_id,
            payload.department_id,
        )

        if assignment is None:
            raise _forbidden(
                "DEPARTMENT_ACCESS_DENIED",
                "You do not have access to this department.",
            )

    return await repository.create(
        db,
        tenant_id=tenant_id,
        college_id=college_id,
        department_id=payload.department_id,
        user_id=payload.user_id,
        designation=payload.designation,
        qualification=payload.qualification,
        joining_date=payload.joining_date,
        research_interests=payload.research_interests,
        bio=payload.bio,
    )


async def list_faculty(
    db: AsyncSession,
    *,
    current_user: User,
    tenant_id: uuid.UUID,
    college_id: uuid.UUID,
    department_id: uuid.UUID | None = None,
) -> list[FacultyProfile]:

    if current_user.role in {
        UserRole.super_admin,
        UserRole.admin,
    }:
        return await repository.list_all(
            db,
            tenant_id,
            college_id,
            department_id=department_id,
        )

    if current_user.role in {
        UserRole.faculty,
        UserRole.hod,
    }:
        from app.modules.user_scope.repository import department_ids

        allowed = await department_ids(
            db,
            tenant_id,
            college_id,
            current_user.id,
        )

        if department_id is not None:
            if department_id not in allowed:
                raise _forbidden(
                    "DEPARTMENT_ACCESS_DENIED",
                    "You do not have access to this department.",
                )

            return await repository.list_all(
                db,
                tenant_id,
                college_id,
                department_id=department_id,
            )

        if not allowed:
            return []

        profiles = await repository.list_all(
            db,
            tenant_id,
            college_id,
        )

        return [
            profile
            for profile in profiles
            if profile.department_id in allowed
        ]

    # Students and parents can view the faculty directory.
    if current_user.role in {
        UserRole.student,
        UserRole.parent,
    }:
        return await repository.list_all(
            db,
            tenant_id,
            college_id,
            department_id=department_id,
        )

    raise _forbidden(
        "FACULTY_ACCESS_DENIED",
        "You do not have access to faculty information.",
    )


async def get_faculty(
    db: AsyncSession,
    *,
    current_user: User,
    tenant_id: uuid.UUID,
    college_id: uuid.UUID,
    faculty_id: uuid.UUID,
) -> FacultyProfile:

    profile = await repository.get_by_id(
        db,
        faculty_id,
        tenant_id,
        college_id,
    )

    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "FACULTY_NOT_FOUND",
                "message": "Faculty profile not found.",
            },
        )

    if current_user.role in {
        UserRole.super_admin,
        UserRole.admin,
        UserRole.student,
        UserRole.parent,
    }:
        return profile

    if current_user.role in {
        UserRole.faculty,
        UserRole.hod,
    }:
        from app.modules.user_scope.repository import department_ids

        allowed = await department_ids(
            db,
            tenant_id,
            college_id,
            current_user.id,
        )

        if profile.department_id not in allowed:
            raise _forbidden(
                "DEPARTMENT_ACCESS_DENIED",
                "You do not have access to this faculty profile.",
            )

        return profile

    raise _forbidden(
        "FACULTY_ACCESS_DENIED",
        "You do not have access to this faculty profile.",
    )


async def get_my_profile(
    db: AsyncSession,
    *,
    current_user: User,
) -> FacultyProfile:

    if current_user.role != UserRole.faculty:
        raise _forbidden(
            "FACULTY_ONLY",
            "This endpoint is available only to faculty users.",
        )

    profile = await repository.get_by_user_id(
        db,
        current_user.id,
        current_user.tenant_id,
        current_user.college_id,
    )

    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "FACULTY_PROFILE_NOT_FOUND",
                "message": "Faculty profile has not been created yet.",
            },
        )

    return profile


async def update_faculty(
    db: AsyncSession,
    *,
    current_user: User,
    profile: FacultyProfile,
    payload: FacultyUpdateRequest,
) -> FacultyProfile:

    if current_user.role == UserRole.faculty:
        if profile.user_id != current_user.id:
            raise _forbidden(
                "FACULTY_PROFILE_ACCESS_DENIED",
                "You can only update your own faculty profile.",
            )

    elif current_user.role == UserRole.hod:
        from app.modules.user_scope.repository import get_assignment

        assignment = await get_assignment(
            db,
            current_user.tenant_id,
            current_user.id,
            current_user.college_id,
            profile.department_id,
        )

        if assignment is None:
            raise _forbidden(
                "DEPARTMENT_ACCESS_DENIED",
                "You do not have access to this faculty profile.",
            )

    elif current_user.role not in {
        UserRole.super_admin,
        UserRole.admin,
    }:
        raise _forbidden(
            "FACULTY_MANAGEMENT_DENIED",
            "You do not have permission to update faculty profiles.",
        )

    if payload.department_id is not None:
        await _validate_department(
            db,
            tenant_id=current_user.tenant_id,
            college_id=current_user.college_id,
            department_id=payload.department_id,
        )

    return await repository.update(
        db,
        profile,
        department_id=payload.department_id,
        designation=payload.designation,
        qualification=payload.qualification,
        joining_date=payload.joining_date,
        research_interests=payload.research_interests,
        bio=payload.bio,
    )

async def _get_accessible_faculty(
    db: AsyncSession,
    *,
    current_user: User,
    tenant_id: uuid.UUID,
    college_id: uuid.UUID,
    faculty_id: uuid.UUID,
) -> FacultyProfile:
    profile = await repository.get_by_id(
        db,
        faculty_id,
        tenant_id,
        college_id,
    )

    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "FACULTY_NOT_FOUND",
                "message": "Faculty profile not found.",
            },
        )

    if current_user.role in {
        UserRole.super_admin,
        UserRole.admin,
    }:
        return profile

    if current_user.role == UserRole.faculty:
        if profile.user_id != current_user.id:
            raise _forbidden(
                "FACULTY_PROFILE_ACCESS_DENIED",
                "You can only manage your own academic records.",
            )
        return profile

    if current_user.role == UserRole.hod:
        from app.modules.user_scope.repository import get_assignment

        assignment = await get_assignment(
            db,
            tenant_id,
            current_user.id,
            college_id,
            profile.department_id,
        )

        if assignment is None:
            raise _forbidden(
                "DEPARTMENT_ACCESS_DENIED",
                "You do not have access to this faculty member.",
            )

        return profile

    raise _forbidden(
        "FACULTY_ACCESS_DENIED",
        "You do not have permission to manage faculty records.",
    )

async def create_achievement(
    db: AsyncSession,
    *,
    current_user: User,
    tenant_id: uuid.UUID,
    college_id: uuid.UUID,
    faculty_id: uuid.UUID,
    payload: FacultyAchievementCreateRequest,
) -> FacultyAchievement:
    await _get_accessible_faculty(
        db,
        current_user=current_user,
        tenant_id=tenant_id,
        college_id=college_id,
        faculty_id=faculty_id,
    )

    return await repository.create_achievement(
        db,
        tenant_id=tenant_id,
        college_id=college_id,
        faculty_id=faculty_id,
        title=payload.title,
        category=payload.category,
        description=payload.description,
        issuing_organization=payload.issuing_organization,
        achievement_date=payload.achievement_date,
        reference_url=payload.reference_url,
    )

async def list_achievements(
    db: AsyncSession,
    *,
    current_user: User,
    tenant_id: uuid.UUID,
    college_id: uuid.UUID,
    faculty_id: uuid.UUID,
) -> list[FacultyAchievement]:
    profile = await repository.get_by_id(
        db,
        faculty_id,
        tenant_id,
        college_id,
    )

    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "FACULTY_NOT_FOUND",
                "message": "Faculty profile not found.",
            },
        )

    if current_user.role in {
        UserRole.super_admin,
        UserRole.admin,
        UserRole.student,
        UserRole.parent,
    }:
        return await repository.list_achievements(
            db,
            faculty_id=faculty_id,
            tenant_id=tenant_id,
            college_id=college_id,
        )

    await _get_accessible_faculty(
        db,
        current_user=current_user,
        tenant_id=tenant_id,
        college_id=college_id,
        faculty_id=faculty_id,
    )

    return await repository.list_achievements(
        db,
        faculty_id=faculty_id,
        tenant_id=tenant_id,
        college_id=college_id,
    )

async def get_achievement(
    db: AsyncSession,
    *,
    current_user: User,
    tenant_id: uuid.UUID,
    college_id: uuid.UUID,
    achievement_id: uuid.UUID,
) -> FacultyAchievement:
    achievement = await repository.get_achievement_by_id(
        db,
        achievement_id=achievement_id,
        tenant_id=tenant_id,
        college_id=college_id,
    )

    if achievement is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "ACHIEVEMENT_NOT_FOUND",
                "message": "Faculty achievement not found.",
            },
        )

    await _get_accessible_faculty(
        db,
        current_user=current_user,
        tenant_id=tenant_id,
        college_id=college_id,
        faculty_id=achievement.faculty_id,
    )

    return achievement

async def update_achievement(
    db: AsyncSession,
    *,
    current_user: User,
    tenant_id: uuid.UUID,
    college_id: uuid.UUID,
    achievement_id: uuid.UUID,
    payload: FacultyAchievementUpdateRequest,
) -> FacultyAchievement:
    achievement = await get_achievement(
        db,
        current_user=current_user,
        tenant_id=tenant_id,
        college_id=college_id,
        achievement_id=achievement_id,
    )

    values = {}

    if payload.title is not None:
        values["title"] = payload.title

    if payload.category is not None:
        values["category"] = payload.category

    if payload.description is not None:
        values["description"] = payload.description

    if payload.issuing_organization is not None:
        values["issuing_organization"] = (
            payload.issuing_organization
        )

    if payload.achievement_date is not None:
        values["achievement_date"] = payload.achievement_date

    if payload.reference_url is not None:
        values["reference_url"] = payload.reference_url

    return await repository.update_achievement(
        db,
        achievement,
        **values,
    )

async def delete_achievement(
    db: AsyncSession,
    *,
    current_user: User,
    tenant_id: uuid.UUID,
    college_id: uuid.UUID,
    achievement_id: uuid.UUID,
) -> None:
    achievement = await get_achievement(
        db,
        current_user=current_user,
        tenant_id=tenant_id,
        college_id=college_id,
        achievement_id=achievement_id,
    )

    await repository.delete_achievement(
        db,
        achievement,
    )

async def create_publication(
    db: AsyncSession,
    *,
    current_user: User,
    tenant_id: uuid.UUID,
    college_id: uuid.UUID,
    faculty_id: uuid.UUID,
    payload: FacultyPublicationCreateRequest,
) -> FacultyPublication:
    await _get_accessible_faculty(
        db,
        current_user=current_user,
        tenant_id=tenant_id,
        college_id=college_id,
        faculty_id=faculty_id,
    )

    return await repository.create_publication(
        db,
        tenant_id=tenant_id,
        college_id=college_id,
        faculty_id=faculty_id,
        title=payload.title,
        publication_type=payload.publication_type,
        journal_or_conference=payload.journal_or_conference,
        publisher=payload.publisher,
        publication_date=payload.publication_date,
        volume=payload.volume,
        issue=payload.issue,
        pages=payload.pages,
        doi=payload.doi,
        indexing=payload.indexing,
        url=payload.url,
        abstract=payload.abstract,
    )

async def list_publications(
    db: AsyncSession,
    *,
    current_user: User,
    tenant_id: uuid.UUID,
    college_id: uuid.UUID,
    faculty_id: uuid.UUID,
) -> list[FacultyPublication]:
    profile = await repository.get_by_id(
        db,
        faculty_id,
        tenant_id,
        college_id,
    )

    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "FACULTY_NOT_FOUND",
                "message": "Faculty profile not found.",
            },
        )

    if current_user.role not in {
        UserRole.super_admin,
        UserRole.admin,
        UserRole.student,
        UserRole.parent,
    }:
        await _get_accessible_faculty(
            db,
            current_user=current_user,
            tenant_id=tenant_id,
            college_id=college_id,
            faculty_id=faculty_id,
        )

    return await repository.list_publications(
        db,
        faculty_id=faculty_id,
        tenant_id=tenant_id,
        college_id=college_id,
    )

async def get_publication(
    db: AsyncSession,
    *,
    current_user: User,
    tenant_id: uuid.UUID,
    college_id: uuid.UUID,
    publication_id: uuid.UUID,
) -> FacultyPublication:
    publication = await repository.get_publication_by_id(
        db,
        publication_id=publication_id,
        tenant_id=tenant_id,
        college_id=college_id,
    )

    if publication is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "PUBLICATION_NOT_FOUND",
                "message": "Faculty publication not found.",
            },
        )

    if current_user.role not in {
        UserRole.super_admin,
        UserRole.admin,
        UserRole.student,
        UserRole.parent,
    }:
        await _get_accessible_faculty(
            db,
            current_user=current_user,
            tenant_id=tenant_id,
            college_id=college_id,
            faculty_id=publication.faculty_id,
        )

    return publication

async def update_publication(
    db: AsyncSession,
    *,
    current_user: User,
    tenant_id: uuid.UUID,
    college_id: uuid.UUID,
    publication_id: uuid.UUID,
    payload: FacultyPublicationUpdateRequest,
) -> FacultyPublication:
    publication = await get_publication(
        db,
        current_user=current_user,
        tenant_id=tenant_id,
        college_id=college_id,
        publication_id=publication_id,
    )

    if current_user.role in {
        UserRole.student,
        UserRole.parent,
    }:
        raise _forbidden(
            "PUBLICATION_UPDATE_DENIED",
            "You do not have permission to modify publications.",
        )

    values = {
        "title": payload.title,
        "publication_type": payload.publication_type,
        "journal_or_conference": payload.journal_or_conference,
        "publisher": payload.publisher,
        "publication_date": payload.publication_date,
        "volume": payload.volume,
        "issue": payload.issue,
        "pages": payload.pages,
        "doi": payload.doi,
        "indexing": payload.indexing,
        "url": payload.url,
        "abstract": payload.abstract,
    }

    values = {
        key: value
        for key, value in values.items()
        if value is not None
    }

    return await repository.update_publication(
        db,
        publication,
        **values,
    )

async def delete_publication(
    db: AsyncSession,
    *,
    current_user: User,
    tenant_id: uuid.UUID,
    college_id: uuid.UUID,
    publication_id: uuid.UUID,
) -> None:
    publication = await get_publication(
        db,
        current_user=current_user,
        tenant_id=tenant_id,
        college_id=college_id,
        publication_id=publication_id,
    )

    if current_user.role in {
        UserRole.student,
        UserRole.parent,
    }:
        raise _forbidden(
            "PUBLICATION_DELETE_DENIED",
            "You do not have permission to delete publications.",
        )

    await repository.delete_publication(
        db,
        publication,
    )

async def create_patent(
    db: AsyncSession,
    *,
    current_user: User,
    tenant_id: uuid.UUID,
    college_id: uuid.UUID,
    faculty_id: uuid.UUID,
    payload: FacultyPatentCreateRequest,
) -> FacultyPatent:
    await _get_accessible_faculty(
        db,
        current_user=current_user,
        tenant_id=tenant_id,
        college_id=college_id,
        faculty_id=faculty_id,
    )

    return await repository.create_patent(
        db,
        tenant_id=tenant_id,
        college_id=college_id,
        faculty_id=faculty_id,
        title=payload.title,
        patent_number=payload.patent_number,
        application_number=payload.application_number,
        patent_type=payload.patent_type,
        status=payload.status,
        filing_date=payload.filing_date,
        publication_date=payload.publication_date,
        grant_date=payload.grant_date,
        inventors=payload.inventors,
        assignee=payload.assignee,
        country=payload.country,
        office=payload.office,
        description=payload.description,
        reference_url=payload.reference_url,
    )

async def list_patents(
    db: AsyncSession,
    *,
    current_user: User,
    tenant_id: uuid.UUID,
    college_id: uuid.UUID,
    faculty_id: uuid.UUID,
) -> list[FacultyPatent]:
    profile = await repository.get_by_id(
        db,
        faculty_id,
        tenant_id,
        college_id,
    )

    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "FACULTY_NOT_FOUND",
                "message": "Faculty profile not found.",
            },
        )

    if current_user.role not in {
        UserRole.super_admin,
        UserRole.admin,
        UserRole.student,
        UserRole.parent,
    }:
        await _get_accessible_faculty(
            db,
            current_user=current_user,
            tenant_id=tenant_id,
            college_id=college_id,
            faculty_id=faculty_id,
        )

    return await repository.list_patents(
        db,
        faculty_id=faculty_id,
        tenant_id=tenant_id,
        college_id=college_id,
    )

async def get_patent(
    db: AsyncSession,
    *,
    current_user: User,
    tenant_id: uuid.UUID,
    college_id: uuid.UUID,
    patent_id: uuid.UUID,
) -> FacultyPatent:
    patent = await repository.get_patent_by_id(
        db,
        patent_id=patent_id,
        tenant_id=tenant_id,
        college_id=college_id,
    )

    if patent is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "PATENT_NOT_FOUND",
                "message": "Faculty patent not found.",
            },
        )

    if current_user.role not in {
        UserRole.super_admin,
        UserRole.admin,
        UserRole.student,
        UserRole.parent,
    }:
        await _get_accessible_faculty(
            db,
            current_user=current_user,
            tenant_id=tenant_id,
            college_id=college_id,
            faculty_id=patent.faculty_id,
        )

    return patent

async def update_patent(
    db: AsyncSession,
    *,
    current_user: User,
    tenant_id: uuid.UUID,
    college_id: uuid.UUID,
    patent_id: uuid.UUID,
    payload: FacultyPatentUpdateRequest,
) -> FacultyPatent:
    patent = await get_patent(
        db,
        current_user=current_user,
        tenant_id=tenant_id,
        college_id=college_id,
        patent_id=patent_id,
    )

    if current_user.role in {
        UserRole.student,
        UserRole.parent,
    }:
        raise _forbidden(
            "PATENT_UPDATE_DENIED",
            "You do not have permission to modify patents.",
        )

    values = {
        "title": payload.title,
        "patent_number": payload.patent_number,
        "application_number": payload.application_number,
        "patent_type": payload.patent_type,
        "status": payload.status,
        "filing_date": payload.filing_date,
        "publication_date": payload.publication_date,
        "grant_date": payload.grant_date,
        "inventors": payload.inventors,
        "assignee": payload.assignee,
        "country": payload.country,
        "office": payload.office,
        "description": payload.description,
        "reference_url": payload.reference_url,
    }

    values = {
        key: value
        for key, value in values.items()
        if value is not None
    }

    return await repository.update_patent(
        db,
        patent,
        **values,
    )

async def delete_patent(
    db: AsyncSession,
    *,
    current_user: User,
    tenant_id: uuid.UUID,
    college_id: uuid.UUID,
    patent_id: uuid.UUID,
) -> None:
    patent = await get_patent(
        db,
        current_user=current_user,
        tenant_id=tenant_id,
        college_id=college_id,
        patent_id=patent_id,
    )

    if current_user.role in {
        UserRole.student,
        UserRole.parent,
    }:
        raise _forbidden(
            "PATENT_DELETE_DENIED",
            "You do not have permission to delete patents.",
        )

    await repository.delete_patent(
        db,
        patent,
    )

async def create_book_chapter(
    db: AsyncSession,
    *,
    current_user: User,
    tenant_id: uuid.UUID,
    college_id: uuid.UUID,
    faculty_id: uuid.UUID,
    payload: FacultyBookChapterCreateRequest,
) -> FacultyBookChapter:
    await _get_accessible_faculty(
        db,
        current_user=current_user,
        tenant_id=tenant_id,
        college_id=college_id,
        faculty_id=faculty_id,
    )

    return await repository.create_book_chapter(
        db,
        tenant_id=tenant_id,
        college_id=college_id,
        faculty_id=faculty_id,
        chapter_title=payload.chapter_title,
        book_title=payload.book_title,
        publisher=payload.publisher,
        publication_date=payload.publication_date,
        isbn=payload.isbn,
        edition=payload.edition,
        chapter_number=payload.chapter_number,
        pages=payload.pages,
        editors=payload.editors,
        doi=payload.doi,
        url=payload.url,
        description=payload.description,
    )

async def list_book_chapters(
    db: AsyncSession,
    *,
    current_user: User,
    tenant_id: uuid.UUID,
    college_id: uuid.UUID,
    faculty_id: uuid.UUID,
) -> list[FacultyBookChapter]:
    profile = await repository.get_by_id(
        db,
        faculty_id,
        tenant_id,
        college_id,
    )

    if profile is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "FACULTY_NOT_FOUND",
                "message": "Faculty profile not found.",
            },
        )

    if current_user.role not in {
        UserRole.super_admin,
        UserRole.admin,
        UserRole.student,
        UserRole.parent,
    }:
        await _get_accessible_faculty(
            db,
            current_user=current_user,
            tenant_id=tenant_id,
            college_id=college_id,
            faculty_id=faculty_id,
        )

    return await repository.list_book_chapters(
        db,
        faculty_id=faculty_id,
        tenant_id=tenant_id,
        college_id=college_id,
    )

async def get_book_chapter(
    db: AsyncSession,
    *,
    current_user: User,
    tenant_id: uuid.UUID,
    college_id: uuid.UUID,
    chapter_id: uuid.UUID,
) -> FacultyBookChapter:
    chapter = await repository.get_book_chapter_by_id(
        db,
        chapter_id=chapter_id,
        tenant_id=tenant_id,
        college_id=college_id,
    )

    if chapter is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "BOOK_CHAPTER_NOT_FOUND",
                "message": "Faculty book chapter not found.",
            },
        )

    if current_user.role not in {
        UserRole.super_admin,
        UserRole.admin,
        UserRole.student,
        UserRole.parent,
    }:
        await _get_accessible_faculty(
            db,
            current_user=current_user,
            tenant_id=tenant_id,
            college_id=college_id,
            faculty_id=chapter.faculty_id,
        )

    return chapter

async def update_book_chapter(
    db: AsyncSession,
    *,
    current_user: User,
    tenant_id: uuid.UUID,
    college_id: uuid.UUID,
    chapter_id: uuid.UUID,
    payload: FacultyBookChapterUpdateRequest,
) -> FacultyBookChapter:
    chapter = await get_book_chapter(
        db,
        current_user=current_user,
        tenant_id=tenant_id,
        college_id=college_id,
        chapter_id=chapter_id,
    )

    if current_user.role in {
        UserRole.student,
        UserRole.parent,
    }:
        raise _forbidden(
            "BOOK_CHAPTER_UPDATE_DENIED",
            "You do not have permission to modify book chapters.",
        )

    values = {
        "chapter_title": payload.chapter_title,
        "book_title": payload.book_title,
        "publisher": payload.publisher,
        "publication_date": payload.publication_date,
        "isbn": payload.isbn,
        "edition": payload.edition,
        "chapter_number": payload.chapter_number,
        "pages": payload.pages,
        "editors": payload.editors,
        "doi": payload.doi,
        "url": payload.url,
        "description": payload.description,
    }

    values = {
        key: value
        for key, value in values.items()
        if value is not None
    }

    return await repository.update_book_chapter(
        db,
        chapter,
        **values,
    )

async def delete_book_chapter(
    db: AsyncSession,
    *,
    current_user: User,
    tenant_id: uuid.UUID,
    college_id: uuid.UUID,
    chapter_id: uuid.UUID,
) -> None:
    chapter = await get_book_chapter(
        db,
        current_user=current_user,
        tenant_id=tenant_id,
        college_id=college_id,
        chapter_id=chapter_id,
    )

    if current_user.role in {
        UserRole.student,
        UserRole.parent,
    }:
        raise _forbidden(
            "BOOK_CHAPTER_DELETE_DENIED",
            "You do not have permission to delete book chapters.",
        )

    await repository.delete_book_chapter(
        db,
        chapter,
    )


async def _get_course_for_college(
    db: AsyncSession,
    *,
    tenant_id: uuid.UUID,
    college_id: uuid.UUID,
    course_id: uuid.UUID,
):
    from app.modules.courses.models import Course

    result = await db.execute(
        select(Course).where(
            Course.id == course_id,
            Course.tenant_id == tenant_id,
            Course.college_id == college_id,
            Course.is_active.is_(True),
        )
    )
    course = result.scalar_one_or_none()
    if course is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "COURSE_NOT_FOUND",
                "message": "Course not found in this college.",
            },
        )
    return course


async def create_course_assignment(
    db: AsyncSession,
    *,
    current_user: User,
    tenant_id: uuid.UUID,
    college_id: uuid.UUID,
    faculty_id: uuid.UUID,
    payload: FacultyCourseAssignmentCreateRequest,
) -> FacultyCourseAssignment:
    profile = await _get_accessible_faculty(
        db, current_user=current_user, tenant_id=tenant_id,
        college_id=college_id, faculty_id=faculty_id,
    )
    course = await _get_course_for_college(
        db, tenant_id=tenant_id, college_id=college_id, course_id=payload.course_id,
    )
    if course.department_id != profile.department_id:
        raise _forbidden(
            "DEPARTMENT_MISMATCH",
            "Faculty and course must belong to the same department.",
        )
    return await repository.create_course_assignment(
        db, tenant_id=tenant_id, college_id=college_id, faculty_id=faculty_id,
        course_id=payload.course_id, academic_year=payload.academic_year,
        semester=payload.semester, section=payload.section,
        teaching_role=payload.teaching_role, assigned_from=payload.assigned_from,
        assigned_until=payload.assigned_until,
    )


async def list_course_assignments(
    db: AsyncSession, *, current_user: User, tenant_id: uuid.UUID,
    college_id: uuid.UUID, faculty_id: uuid.UUID,
) -> list[FacultyCourseAssignment]:
    profile = await repository.get_by_id(db, faculty_id, tenant_id, college_id)
    if profile is None:
        raise HTTPException(status_code=404, detail={"code":"FACULTY_NOT_FOUND","message":"Faculty profile not found."})
    if current_user.role not in {UserRole.super_admin, UserRole.admin, UserRole.student, UserRole.parent}:
        await _get_accessible_faculty(db, current_user=current_user, tenant_id=tenant_id, college_id=college_id, faculty_id=faculty_id)
    return await repository.list_course_assignments(db, faculty_id=faculty_id, tenant_id=tenant_id, college_id=college_id)


async def get_course_assignment(
    db: AsyncSession, *, current_user: User, tenant_id: uuid.UUID,
    college_id: uuid.UUID, assignment_id: uuid.UUID,
) -> FacultyCourseAssignment:
    assignment = await repository.get_course_assignment_by_id(db, assignment_id=assignment_id, tenant_id=tenant_id, college_id=college_id)
    if assignment is None:
        raise HTTPException(status_code=404, detail={"code":"COURSE_ASSIGNMENT_NOT_FOUND","message":"Faculty course assignment not found."})
    await _get_accessible_faculty(db, current_user=current_user, tenant_id=tenant_id, college_id=college_id, faculty_id=assignment.faculty_id)
    return assignment


async def update_course_assignment(
    db: AsyncSession, *, current_user: User, tenant_id: uuid.UUID, college_id: uuid.UUID,
    assignment_id: uuid.UUID, payload: FacultyCourseAssignmentUpdateRequest,
) -> FacultyCourseAssignment:
    assignment = await get_course_assignment(db, current_user=current_user, tenant_id=tenant_id, college_id=college_id, assignment_id=assignment_id)
    if payload.course_id is not None:
        course = await _get_course_for_college(db, tenant_id=tenant_id, college_id=college_id, course_id=payload.course_id)
        profile = await repository.get_by_id(db, assignment.faculty_id, tenant_id, college_id)
        if profile and course.department_id != profile.department_id:
            raise _forbidden("DEPARTMENT_MISMATCH", "Faculty and course must belong to the same department.")
    values = {k:v for k,v in payload.model_dump().items() if v is not None}
    return await repository.update_course_assignment(db, assignment, **values)


async def delete_course_assignment(
    db: AsyncSession, *, current_user: User, tenant_id: uuid.UUID, college_id: uuid.UUID, assignment_id: uuid.UUID,
) -> None:
    assignment = await get_course_assignment(db, current_user=current_user, tenant_id=tenant_id, college_id=college_id, assignment_id=assignment_id)
    await repository.delete_course_assignment(db, assignment)


async def create_fdp(
    db: AsyncSession, *, current_user: User, tenant_id: uuid.UUID, college_id: uuid.UUID,
    faculty_id: uuid.UUID, payload: FacultyDevelopmentProgramCreateRequest,
) -> FacultyDevelopmentProgram:
    await _get_accessible_faculty(db, current_user=current_user, tenant_id=tenant_id, college_id=college_id, faculty_id=faculty_id)
    if payload.start_date and payload.end_date and payload.end_date < payload.start_date:
        raise HTTPException(status_code=422, detail={"code":"INVALID_DATE_RANGE","message":"End date cannot be before start date."})
    return await repository.create_fdp(
        db, tenant_id=tenant_id, college_id=college_id, faculty_id=faculty_id,
        title=payload.title, organizer=payload.organizer, program_type=payload.program_type,
        mode=payload.mode, venue=payload.venue, start_date=payload.start_date, end_date=payload.end_date,
        duration_hours=payload.duration_hours, certificate_number=payload.certificate_number,
        certificate_url=payload.certificate_url, description=payload.description,
    )


async def list_fdps(
    db: AsyncSession, *, current_user: User, tenant_id: uuid.UUID, college_id: uuid.UUID, faculty_id: uuid.UUID,
) -> list[FacultyDevelopmentProgram]:
    profile = await repository.get_by_id(db, faculty_id, tenant_id, college_id)
    if profile is None:
        raise HTTPException(status_code=404, detail={"code":"FACULTY_NOT_FOUND","message":"Faculty profile not found."})
    if current_user.role not in {UserRole.super_admin, UserRole.admin, UserRole.student, UserRole.parent}:
        await _get_accessible_faculty(db, current_user=current_user, tenant_id=tenant_id, college_id=college_id, faculty_id=faculty_id)
    return await repository.list_fdps(db, faculty_id=faculty_id, tenant_id=tenant_id, college_id=college_id)


async def get_fdp(
    db: AsyncSession, *, current_user: User, tenant_id: uuid.UUID, college_id: uuid.UUID, fdp_id: uuid.UUID,
) -> FacultyDevelopmentProgram:
    fdp = await repository.get_fdp_by_id(db, fdp_id=fdp_id, tenant_id=tenant_id, college_id=college_id)
    if fdp is None:
        raise HTTPException(status_code=404, detail={"code":"FDP_NOT_FOUND","message":"Faculty development program not found."})
    if current_user.role not in {UserRole.super_admin, UserRole.admin, UserRole.student, UserRole.parent}:
        await _get_accessible_faculty(db, current_user=current_user, tenant_id=tenant_id, college_id=college_id, faculty_id=fdp.faculty_id)
    return fdp


async def update_fdp(
    db: AsyncSession, *, current_user: User, tenant_id: uuid.UUID, college_id: uuid.UUID, fdp_id: uuid.UUID,
    payload: FacultyDevelopmentProgramUpdateRequest,
) -> FacultyDevelopmentProgram:
    fdp = await get_fdp(db, current_user=current_user, tenant_id=tenant_id, college_id=college_id, fdp_id=fdp_id)
    if current_user.role in {UserRole.student, UserRole.parent}:
        raise _forbidden("FDP_UPDATE_DENIED", "You do not have permission to modify FDP records.")
    if payload.start_date and payload.end_date and payload.end_date < payload.start_date:
        raise HTTPException(status_code=422, detail={"code":"INVALID_DATE_RANGE","message":"End date cannot be before start date."})
    values = {k:v for k,v in payload.model_dump().items() if v is not None}
    return await repository.update_fdp(db, fdp, **values)


async def delete_fdp(
    db: AsyncSession, *, current_user: User, tenant_id: uuid.UUID, college_id: uuid.UUID, fdp_id: uuid.UUID,
) -> None:
    fdp = await get_fdp(db, current_user=current_user, tenant_id=tenant_id, college_id=college_id, fdp_id=fdp_id)
    if current_user.role in {UserRole.student, UserRole.parent}:
        raise _forbidden("FDP_DELETE_DENIED", "You do not have permission to delete FDP records.")
    await repository.delete_fdp(db, fdp)
