"""Faculty router."""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.dependencies import get_college, get_current_user, get_tenant
from app.modules.colleges.models import College
from app.modules.faculty import service
from app.modules.faculty.schemas import (
    FacultyAchievementCreateRequest,
    FacultyAchievementResponse,
    FacultyAchievementUpdateRequest,
    FacultyCreateRequest,
    FacultyProfileResponse,
    FacultyPublicationCreateRequest,
    FacultyPublicationResponse,
    FacultyPublicationUpdateRequest,
    FacultyUpdateRequest,
    FacultyPatentCreateRequest,
    FacultyPatentResponse,
    FacultyPatentUpdateRequest,
    FacultyBookChapterCreateRequest,
    FacultyBookChapterResponse,
    FacultyBookChapterUpdateRequest,
    FacultyCourseAssignmentCreateRequest,
    FacultyCourseAssignmentResponse,
    FacultyCourseAssignmentUpdateRequest,
    FacultyDevelopmentProgramCreateRequest,
    FacultyDevelopmentProgramResponse,
    FacultyDevelopmentProgramUpdateRequest,
)
from app.modules.tenants.models import Tenant
from app.modules.users.models import User

router = APIRouter(
    prefix="/faculty",
    tags=["faculty"],
)


@router.post(
    "",
    response_model=FacultyProfileResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_faculty(
    payload: FacultyCreateRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    tenant: Annotated[Tenant, Depends(get_tenant)],
    college: Annotated[College, Depends(get_college)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> FacultyProfileResponse:
    profile = await service.create_faculty(
        db,
        current_user=current_user,
        tenant_id=tenant.id,
        college_id=college.id,
        payload=payload,
    )

    return FacultyProfileResponse.model_validate(profile)


@router.get(
    "",
    response_model=list[FacultyProfileResponse],
)
async def list_faculty(
    db: Annotated[AsyncSession, Depends(get_db)],
    tenant: Annotated[Tenant, Depends(get_tenant)],
    college: Annotated[College, Depends(get_college)],
    current_user: Annotated[User, Depends(get_current_user)],
    department_id: uuid.UUID | None = Query(default=None),
) -> list[FacultyProfileResponse]:
    profiles = await service.list_faculty(
        db,
        current_user=current_user,
        tenant_id=tenant.id,
        college_id=college.id,
        department_id=department_id,
    )

    return [
        FacultyProfileResponse.model_validate(profile)
        for profile in profiles
    ]


@router.get(
    "/me",
    response_model=FacultyProfileResponse,
)
async def get_my_faculty_profile(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> FacultyProfileResponse:
    profile = await service.get_my_profile(
        db,
        current_user=current_user,
    )

    return FacultyProfileResponse.model_validate(profile)

@router.patch(
    "/me",
    response_model=FacultyProfileResponse,
)
async def update_my_faculty_profile(
    payload: FacultyUpdateRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> FacultyProfileResponse:
    profile = await service.get_my_profile(
        db,
        current_user=current_user,
    )

    updated = await service.update_faculty(
        db,
        current_user=current_user,
        profile=profile,
        payload=payload,
    )

    return FacultyProfileResponse.model_validate(updated)

@router.get(
    "/{faculty_id}",
    response_model=FacultyProfileResponse,
)
async def get_faculty(
    faculty_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    tenant: Annotated[Tenant, Depends(get_tenant)],
    college: Annotated[College, Depends(get_college)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> FacultyProfileResponse:
    profile = await service.get_faculty(
        db,
        current_user=current_user,
        tenant_id=tenant.id,
        college_id=college.id,
        faculty_id=faculty_id,
    )

    return FacultyProfileResponse.model_validate(profile)


@router.patch(
    "/{faculty_id}",
    response_model=FacultyProfileResponse,
)
async def update_faculty(
    faculty_id: uuid.UUID,
    payload: FacultyUpdateRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    tenant: Annotated[Tenant, Depends(get_tenant)],
    college: Annotated[College, Depends(get_college)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> FacultyProfileResponse:
    profile = await service.get_faculty(
        db,
        current_user=current_user,
        tenant_id=tenant.id,
        college_id=college.id,
        faculty_id=faculty_id,
    )

    updated = await service.update_faculty(
        db,
        current_user=current_user,
        profile=profile,
        payload=payload,
    )

    return FacultyProfileResponse.model_validate(updated)

@router.post(
    "/{faculty_id}/achievements",
    response_model=FacultyAchievementResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_achievement(
    faculty_id: uuid.UUID,
    payload: FacultyAchievementCreateRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    tenant: Annotated[Tenant, Depends(get_tenant)],
    college: Annotated[College, Depends(get_college)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> FacultyAchievementResponse:
    achievement = await service.create_achievement(
        db,
        current_user=current_user,
        tenant_id=tenant.id,
        college_id=college.id,
        faculty_id=faculty_id,
        payload=payload,
    )

    return FacultyAchievementResponse.model_validate(
        achievement
    )

@router.get(
    "/{faculty_id}/achievements",
    response_model=list[FacultyAchievementResponse],
)
async def list_achievements(
    faculty_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    tenant: Annotated[Tenant, Depends(get_tenant)],
    college: Annotated[College, Depends(get_college)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> list[FacultyAchievementResponse]:
    achievements = await service.list_achievements(
        db,
        current_user=current_user,
        tenant_id=tenant.id,
        college_id=college.id,
        faculty_id=faculty_id,
    )

    return [
        FacultyAchievementResponse.model_validate(item)
        for item in achievements
    ]

@router.get(
    "/achievements/{achievement_id}",
    response_model=FacultyAchievementResponse,
)
async def get_achievement(
    achievement_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    tenant: Annotated[Tenant, Depends(get_tenant)],
    college: Annotated[College, Depends(get_college)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> FacultyAchievementResponse:
    achievement = await service.get_achievement(
        db,
        current_user=current_user,
        tenant_id=tenant.id,
        college_id=college.id,
        achievement_id=achievement_id,
    )

    return FacultyAchievementResponse.model_validate(
        achievement
    )

@router.patch(
    "/achievements/{achievement_id}",
    response_model=FacultyAchievementResponse,
)
async def update_achievement(
    achievement_id: uuid.UUID,
    payload: FacultyAchievementUpdateRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    tenant: Annotated[Tenant, Depends(get_tenant)],
    college: Annotated[College, Depends(get_college)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> FacultyAchievementResponse:
    achievement = await service.update_achievement(
        db,
        current_user=current_user,
        tenant_id=tenant.id,
        college_id=college.id,
        achievement_id=achievement_id,
        payload=payload,
    )

    return FacultyAchievementResponse.model_validate(
        achievement
    )

@router.delete(
    "/achievements/{achievement_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_achievement(
    achievement_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    tenant: Annotated[Tenant, Depends(get_tenant)],
    college: Annotated[College, Depends(get_college)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> None:
    await service.delete_achievement(
        db,
        current_user=current_user,
        tenant_id=tenant.id,
        college_id=college.id,
        achievement_id=achievement_id,
    )

@router.post(
    "/{faculty_id}/publications",
    response_model=FacultyPublicationResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_publication(
    faculty_id: uuid.UUID,
    payload: FacultyPublicationCreateRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    tenant: Annotated[Tenant, Depends(get_tenant)],
    college: Annotated[College, Depends(get_college)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> FacultyPublicationResponse:
    publication = await service.create_publication(
        db,
        current_user=current_user,
        tenant_id=tenant.id,
        college_id=college.id,
        faculty_id=faculty_id,
        payload=payload,
    )

    return FacultyPublicationResponse.model_validate(
        publication
    )

@router.get(
    "/{faculty_id}/publications",
    response_model=list[FacultyPublicationResponse],
)
async def list_publications(
    faculty_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    tenant: Annotated[Tenant, Depends(get_tenant)],
    college: Annotated[College, Depends(get_college)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> list[FacultyPublicationResponse]:
    publications = await service.list_publications(
        db,
        current_user=current_user,
        tenant_id=tenant.id,
        college_id=college.id,
        faculty_id=faculty_id,
    )

    return [
        FacultyPublicationResponse.model_validate(
            publication
        )
        for publication in publications
    ]

@router.get(
    "/publications/{publication_id}",
    response_model=FacultyPublicationResponse,
)
async def get_publication(
    publication_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    tenant: Annotated[Tenant, Depends(get_tenant)],
    college: Annotated[College, Depends(get_college)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> FacultyPublicationResponse:
    publication = await service.get_publication(
        db,
        current_user=current_user,
        tenant_id=tenant.id,
        college_id=college.id,
        publication_id=publication_id,
    )

    return FacultyPublicationResponse.model_validate(
        publication
    )

@router.patch(
    "/publications/{publication_id}",
    response_model=FacultyPublicationResponse,
)
async def update_publication(
    publication_id: uuid.UUID,
    payload: FacultyPublicationUpdateRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    tenant: Annotated[Tenant, Depends(get_tenant)],
    college: Annotated[College, Depends(get_college)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> FacultyPublicationResponse:
    publication = await service.update_publication(
        db,
        current_user=current_user,
        tenant_id=tenant.id,
        college_id=college.id,
        publication_id=publication_id,
        payload=payload,
    )

    return FacultyPublicationResponse.model_validate(
        publication
    )

@router.delete(
    "/publications/{publication_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_publication(
    publication_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    tenant: Annotated[Tenant, Depends(get_tenant)],
    college: Annotated[College, Depends(get_college)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> None:
    await service.delete_publication(
        db,
        current_user=current_user,
        tenant_id=tenant.id,
        college_id=college.id,
        publication_id=publication_id,
    )

@router.post(
    "/{faculty_id}/patents",
    response_model=FacultyPatentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_patent(
    faculty_id: uuid.UUID,
    payload: FacultyPatentCreateRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    tenant: Annotated[Tenant, Depends(get_tenant)],
    college: Annotated[College, Depends(get_college)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> FacultyPatentResponse:
    patent = await service.create_patent(
        db,
        current_user=current_user,
        tenant_id=tenant.id,
        college_id=college.id,
        faculty_id=faculty_id,
        payload=payload,
    )

    return FacultyPatentResponse.model_validate(patent)

@router.get(
    "/{faculty_id}/patents",
    response_model=list[FacultyPatentResponse],
)
async def list_patents(
    faculty_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    tenant: Annotated[Tenant, Depends(get_tenant)],
    college: Annotated[College, Depends(get_college)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> list[FacultyPatentResponse]:
    patents = await service.list_patents(
        db,
        current_user=current_user,
        tenant_id=tenant.id,
        college_id=college.id,
        faculty_id=faculty_id,
    )

    return [
        FacultyPatentResponse.model_validate(patent)
        for patent in patents
    ]

@router.get(
    "/patents/{patent_id}",
    response_model=FacultyPatentResponse,
)
async def get_patent(
    patent_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    tenant: Annotated[Tenant, Depends(get_tenant)],
    college: Annotated[College, Depends(get_college)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> FacultyPatentResponse:
    patent = await service.get_patent(
        db,
        current_user=current_user,
        tenant_id=tenant.id,
        college_id=college.id,
        patent_id=patent_id,
    )

    return FacultyPatentResponse.model_validate(patent)

@router.patch(
    "/patents/{patent_id}",
    response_model=FacultyPatentResponse,
)
async def update_patent(
    patent_id: uuid.UUID,
    payload: FacultyPatentUpdateRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    tenant: Annotated[Tenant, Depends(get_tenant)],
    college: Annotated[College, Depends(get_college)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> FacultyPatentResponse:
    patent = await service.update_patent(
        db,
        current_user=current_user,
        tenant_id=tenant.id,
        college_id=college.id,
        patent_id=patent_id,
        payload=payload,
    )

    return FacultyPatentResponse.model_validate(patent)

@router.delete(
    "/patents/{patent_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_patent(
    patent_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    tenant: Annotated[Tenant, Depends(get_tenant)],
    college: Annotated[College, Depends(get_college)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> None:
    await service.delete_patent(
        db,
        current_user=current_user,
        tenant_id=tenant.id,
        college_id=college.id,
        patent_id=patent_id,
    )

@router.post(
    "/{faculty_id}/book-chapters",
    response_model=FacultyBookChapterResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_book_chapter(
    faculty_id: uuid.UUID,
    payload: FacultyBookChapterCreateRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    tenant: Annotated[Tenant, Depends(get_tenant)],
    college: Annotated[College, Depends(get_college)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> FacultyBookChapterResponse:
    chapter = await service.create_book_chapter(
        db,
        current_user=current_user,
        tenant_id=tenant.id,
        college_id=college.id,
        faculty_id=faculty_id,
        payload=payload,
    )

    return FacultyBookChapterResponse.model_validate(chapter)

@router.get(
    "/{faculty_id}/book-chapters",
    response_model=list[FacultyBookChapterResponse],
)
async def list_book_chapters(
    faculty_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    tenant: Annotated[Tenant, Depends(get_tenant)],
    college: Annotated[College, Depends(get_college)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> list[FacultyBookChapterResponse]:
    chapters = await service.list_book_chapters(
        db,
        current_user=current_user,
        tenant_id=tenant.id,
        college_id=college.id,
        faculty_id=faculty_id,
    )

    return [
        FacultyBookChapterResponse.model_validate(chapter)
        for chapter in chapters
    ]

@router.get(
    "/book-chapters/{chapter_id}",
    response_model=FacultyBookChapterResponse,
)
async def get_book_chapter(
    chapter_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    tenant: Annotated[Tenant, Depends(get_tenant)],
    college: Annotated[College, Depends(get_college)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> FacultyBookChapterResponse:
    chapter = await service.get_book_chapter(
        db,
        current_user=current_user,
        tenant_id=tenant.id,
        college_id=college.id,
        chapter_id=chapter_id,
    )

    return FacultyBookChapterResponse.model_validate(chapter)

@router.patch(
    "/book-chapters/{chapter_id}",
    response_model=FacultyBookChapterResponse,
)
async def update_book_chapter(
    chapter_id: uuid.UUID,
    payload: FacultyBookChapterUpdateRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    tenant: Annotated[Tenant, Depends(get_tenant)],
    college: Annotated[College, Depends(get_college)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> FacultyBookChapterResponse:
    chapter = await service.update_book_chapter(
        db,
        current_user=current_user,
        tenant_id=tenant.id,
        college_id=college.id,
        chapter_id=chapter_id,
        payload=payload,
    )

    return FacultyBookChapterResponse.model_validate(chapter)

@router.delete(
    "/book-chapters/{chapter_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_book_chapter(
    chapter_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    tenant: Annotated[Tenant, Depends(get_tenant)],
    college: Annotated[College, Depends(get_college)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> None:
    await service.delete_book_chapter(
        db,
        current_user=current_user,
        tenant_id=tenant.id,
        college_id=college.id,
        chapter_id=chapter_id,
    )

@router.post(
    "/{faculty_id}/course-assignments",
    response_model=FacultyCourseAssignmentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_course_assignment(
    faculty_id: uuid.UUID,
    payload: FacultyCourseAssignmentCreateRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    tenant: Annotated[Tenant, Depends(get_tenant)],
    college: Annotated[College, Depends(get_college)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> FacultyCourseAssignmentResponse:
    assignment = await service.create_course_assignment(
        db, current_user=current_user, tenant_id=tenant.id, college_id=college.id,
        faculty_id=faculty_id, payload=payload,
    )
    return FacultyCourseAssignmentResponse.model_validate(assignment)


@router.get(
    "/{faculty_id}/course-assignments",
    response_model=list[FacultyCourseAssignmentResponse],
)
async def list_course_assignments(
    faculty_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    tenant: Annotated[Tenant, Depends(get_tenant)],
    college: Annotated[College, Depends(get_college)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> list[FacultyCourseAssignmentResponse]:
    assignments = await service.list_course_assignments(
        db, current_user=current_user, tenant_id=tenant.id, college_id=college.id, faculty_id=faculty_id,
    )
    return [FacultyCourseAssignmentResponse.model_validate(item) for item in assignments]


@router.get(
    "/course-assignments/{assignment_id}",
    response_model=FacultyCourseAssignmentResponse,
)
async def get_course_assignment(
    assignment_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    tenant: Annotated[Tenant, Depends(get_tenant)],
    college: Annotated[College, Depends(get_college)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> FacultyCourseAssignmentResponse:
    assignment = await service.get_course_assignment(
        db, current_user=current_user, tenant_id=tenant.id, college_id=college.id, assignment_id=assignment_id,
    )
    return FacultyCourseAssignmentResponse.model_validate(assignment)


@router.patch(
    "/course-assignments/{assignment_id}",
    response_model=FacultyCourseAssignmentResponse,
)
async def update_course_assignment(
    assignment_id: uuid.UUID,
    payload: FacultyCourseAssignmentUpdateRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    tenant: Annotated[Tenant, Depends(get_tenant)],
    college: Annotated[College, Depends(get_college)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> FacultyCourseAssignmentResponse:
    assignment = await service.update_course_assignment(
        db, current_user=current_user, tenant_id=tenant.id, college_id=college.id, assignment_id=assignment_id, payload=payload,
    )
    return FacultyCourseAssignmentResponse.model_validate(assignment)


@router.delete(
    "/course-assignments/{assignment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_course_assignment(
    assignment_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    tenant: Annotated[Tenant, Depends(get_tenant)],
    college: Annotated[College, Depends(get_college)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> None:
    await service.delete_course_assignment(
        db, current_user=current_user, tenant_id=tenant.id, college_id=college.id, assignment_id=assignment_id,
    )


@router.post(
    "/{faculty_id}/fdps",
    response_model=FacultyDevelopmentProgramResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_fdp(
    faculty_id: uuid.UUID,
    payload: FacultyDevelopmentProgramCreateRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    tenant: Annotated[Tenant, Depends(get_tenant)],
    college: Annotated[College, Depends(get_college)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> FacultyDevelopmentProgramResponse:
    fdp = await service.create_fdp(
        db, current_user=current_user, tenant_id=tenant.id, college_id=college.id, faculty_id=faculty_id, payload=payload,
    )
    return FacultyDevelopmentProgramResponse.model_validate(fdp)


@router.get(
    "/{faculty_id}/fdps",
    response_model=list[FacultyDevelopmentProgramResponse],
)
async def list_fdps(
    faculty_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    tenant: Annotated[Tenant, Depends(get_tenant)],
    college: Annotated[College, Depends(get_college)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> list[FacultyDevelopmentProgramResponse]:
    fdps = await service.list_fdps(
        db, current_user=current_user, tenant_id=tenant.id, college_id=college.id, faculty_id=faculty_id,
    )
    return [FacultyDevelopmentProgramResponse.model_validate(item) for item in fdps]


@router.get(
    "/fdps/{fdp_id}",
    response_model=FacultyDevelopmentProgramResponse,
)
async def get_fdp(
    fdp_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    tenant: Annotated[Tenant, Depends(get_tenant)],
    college: Annotated[College, Depends(get_college)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> FacultyDevelopmentProgramResponse:
    fdp = await service.get_fdp(
        db, current_user=current_user, tenant_id=tenant.id, college_id=college.id, fdp_id=fdp_id,
    )
    return FacultyDevelopmentProgramResponse.model_validate(fdp)


@router.patch(
    "/fdps/{fdp_id}",
    response_model=FacultyDevelopmentProgramResponse,
)
async def update_fdp(
    fdp_id: uuid.UUID,
    payload: FacultyDevelopmentProgramUpdateRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    tenant: Annotated[Tenant, Depends(get_tenant)],
    college: Annotated[College, Depends(get_college)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> FacultyDevelopmentProgramResponse:
    fdp = await service.update_fdp(
        db, current_user=current_user, tenant_id=tenant.id, college_id=college.id, fdp_id=fdp_id, payload=payload,
    )
    return FacultyDevelopmentProgramResponse.model_validate(fdp)


@router.delete(
    "/fdps/{fdp_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_fdp(
    fdp_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    tenant: Annotated[Tenant, Depends(get_tenant)],
    college: Annotated[College, Depends(get_college)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> None:
    await service.delete_fdp(
        db, current_user=current_user, tenant_id=tenant.id, college_id=college.id, fdp_id=fdp_id,
    )

