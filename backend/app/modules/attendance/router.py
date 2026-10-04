import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.dependencies import get_college, get_current_user, require_module
from app.modules.attendance import repository, service
from app.modules.colleges.models import College
from app.modules.users.models import User, UserRole

from app.modules.attendance.schemas import (
    AttendanceRecordResponse,
    AttendanceSessionCreateRequest,
    AttendanceSessionResponse,
    AttendanceSummaryResponse,
    BulkAttendanceRequest,
    CourseEnrollmentCreateRequest,
    CourseEnrollmentResponse,
    CourseEnrollmentCreateRequest,
    CourseEnrollmentResponse,
)

from app.modules.courses.models import Course

_module_access = require_module("attendance")

router = APIRouter(
    prefix="/attendance",
    tags=["attendance"],
    dependencies=[Depends(_module_access)],
)


@router.post(
    "/enrollments",
    response_model=CourseEnrollmentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_enrollment(
    payload: CourseEnrollmentCreateRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    college: Annotated[College, Depends(get_college)],
) -> CourseEnrollmentResponse:
    enrollment = await service.create_enrollment(
        db,
        current_user=current_user,
        tenant_id=college.tenant_id,
        college_id=college.id,
        course_id=payload.course_id,
        student_id=payload.student_id,
    )

    return CourseEnrollmentResponse.model_validate(
        enrollment
    )


@router.get(
    "/enrollments",
    response_model=list[CourseEnrollmentResponse],
)
async def list_enrollments(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    college: Annotated[College, Depends(get_college)],
    course_id: uuid.UUID | None = Query(default=None),
    student_id: uuid.UUID | None = Query(default=None),
) -> list[CourseEnrollmentResponse]:
    enrollments = await repository.list_enrollments(
        db,
        college.tenant_id,
        college.id,
        course_id=course_id,
        student_id=student_id,
    )

    # Students may only ask for their own enrollment.
    if current_user.role.value == "student":
        from app.modules.students.models import Student

        result = await db.execute(
            select(Student).where(
                Student.user_id == current_user.id,
                Student.tenant_id == college.tenant_id,
                Student.college_id == college.id,
            )
        )
        student = result.scalar_one_or_none()

        if student is None:
            return []

        enrollments = [
            item
            for item in enrollments
            if item.student_id == student.id
        ]

    return [
        CourseEnrollmentResponse.model_validate(item)
        for item in enrollments
    ]

@router.post(
    "/sessions",
    response_model=AttendanceSessionResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_attendance_session(
    payload: AttendanceSessionCreateRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    college: Annotated[College, Depends(get_college)],
) -> AttendanceSessionResponse:
    session = await service.create_attendance_session(
        db,
        current_user=current_user,
        tenant_id=college.tenant_id,
        college_id=college.id,
        course_id=payload.course_id,
        held_on=payload.held_on,
        period=payload.period,
    )

    return AttendanceSessionResponse.model_validate(session)

@router.get(
    "/sessions",
    response_model=list[AttendanceSessionResponse],
)
async def list_attendance_sessions(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    college: Annotated[College, Depends(get_college)],
    course_id: uuid.UUID | None = Query(default=None),
) -> list[AttendanceSessionResponse]:

    sessions = await repository.list_sessions(
        db,
        college.tenant_id,
        college.id,
        course_id=course_id,
    )

    if current_user.role == UserRole.faculty:
        sessions = [
            session
            for session in sessions
            if session.faculty_id == current_user.id
        ]

    return [
        AttendanceSessionResponse.model_validate(session)
        for session in sessions
    ]

@router.post(
    "/sessions/{session_id}/records",
    response_model=list[AttendanceRecordResponse],
)
async def mark_attendance(
    session_id: uuid.UUID,
    payload: BulkAttendanceRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    college: Annotated[College, Depends(get_college)],
) -> list[AttendanceRecordResponse]:

    records = await service.mark_attendance(
        db,
        current_user=current_user,
        tenant_id=college.tenant_id,
        college_id=college.id,
        session_id=session_id,
        records=[
            (record.student_id, record.status.value)
            for record in payload.records
        ],
    )

    return [
        AttendanceRecordResponse.model_validate(record)
        for record in records
    ]

@router.get(
    "/summary",
    response_model=AttendanceSummaryResponse,
)
async def attendance_summary(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    college: Annotated[College, Depends(get_college)],
    student_id: uuid.UUID | None = Query(default=None),
) -> AttendanceSummaryResponse:

    summary = await service.get_student_summary(
        db,
        current_user=current_user,
        tenant_id=college.tenant_id,
        college_id=college.id,
        student_id=student_id,
    )

    return AttendanceSummaryResponse(**summary)

@router.delete(
    "/enrollments/{enrollment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_enrollment(
    enrollment_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    college: Annotated[College, Depends(get_college)],
) -> None:
    await service.remove_enrollment(
        db,
        current_user=current_user,
        tenant_id=college.tenant_id,
        college_id=college.id,
        enrollment_id=enrollment_id,
    )

@router.get(
    "/courses/{course_id}/students",
    response_model=list[CourseEnrollmentResponse],
)
async def list_course_students(
    course_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    college: Annotated[College, Depends(get_college)],
) -> list[CourseEnrollmentResponse]:
    course_result = await db.execute(
        select(Course).where(
            Course.id == course_id,
            Course.tenant_id == college.tenant_id,
            Course.college_id == college.id,
            Course.is_active.is_(True),
        )
    )

    course = course_result.scalar_one_or_none()

    if course is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "COURSE_NOT_FOUND",
                "message": "Course not found in this college.",
            },
        )

    if current_user.role == UserRole.faculty:
        if course.faculty_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "code": "COURSE_ACCESS_DENIED",
                    "message": "You do not have access to this course.",
                },
            )

    enrollments = await repository.list_course_enrollments(
        db,
        college.tenant_id,
        college.id,
        course_id,
    )

    return [
        CourseEnrollmentResponse.model_validate(item)
        for item in enrollments
    ]

@router.get(
    "/sessions/{session_id}/records",
    response_model=list[AttendanceRecordResponse],
)
async def list_session_records(
    session_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
    college: Annotated[College, Depends(get_college)],
) -> list[AttendanceRecordResponse]:
    session = await repository.get_session(
        db,
        college.tenant_id,
        college.id,
        session_id,
    )

    if session is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "ATTENDANCE_SESSION_NOT_FOUND",
                "message": "Attendance session not found.",
            },
        )

    course_result = await db.execute(
        select(Course).where(
            Course.id == session.course_id,
            Course.tenant_id == college.tenant_id,
            Course.college_id == college.id,
        )
    )

    course = course_result.scalar_one_or_none()

    if course is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "COURSE_NOT_FOUND",
                "message": "Course not found.",
            },
        )

    if current_user.role == UserRole.faculty:
        if session.faculty_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "code": "ATTENDANCE_SESSION_ACCESS_DENIED",
                    "message": "You do not have access to this attendance session.",
                },
            )

    elif current_user.role == UserRole.hod:
        from app.modules.user_scope.repository import get_assignment

        assignment = await get_assignment(
            db,
            college.tenant_id,
            current_user.id,
            college.id,
            course.department_id,
        )

        if assignment is None:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "code": "DEPARTMENT_ACCESS_DENIED",
                    "message": "You do not have access to this attendance session.",
                },
            )

    elif current_user.role not in {
        UserRole.super_admin,
        UserRole.admin,
    }:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "code": "ATTENDANCE_SESSION_ACCESS_DENIED",
                "message": "You do not have access to this attendance session.",
            },
        )

    records = await repository.list_session_records(
        db,
        college.tenant_id,
        college.id,
        session_id,
    )

    return [
        AttendanceRecordResponse.model_validate(record)
        for record in records
    ]