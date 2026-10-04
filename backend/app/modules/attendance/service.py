import uuid

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.attendance import repository
from app.modules.attendance.models import (
    AttendanceRecord,
    AttendanceSession,
    CourseEnrollment,
)

from app.modules.courses.models import Course
from app.modules.students.models import Student
from app.modules.users.models import User, UserRole
from datetime import date


def _forbidden(code: str, message: str) -> HTTPException:
    return HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail={
            "code": code,
            "message": message,
        },
    )


async def create_enrollment(
    db: AsyncSession,
    *,
    current_user: User,
    tenant_id: uuid.UUID,
    college_id: uuid.UUID,
    course_id: uuid.UUID,
    student_id: uuid.UUID,
) -> CourseEnrollment:

    # Verify course belongs to this tenant + college.
    course_result = await db.execute(
        select(Course).where(
            Course.id == course_id,
            Course.tenant_id == tenant_id,
            Course.college_id == college_id,
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

    # Verify student belongs to the same tenant + college.
    student_result = await db.execute(
        select(Student).where(
            Student.id == student_id,
            Student.tenant_id == tenant_id,
            Student.college_id == college_id,
        )
    )
    student = student_result.scalar_one_or_none()

    if student is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "STUDENT_NOT_FOUND",
                "message": "Student not found in this college.",
            },
        )

    # Only administrative/scoped academic roles may create enrollments.
    if current_user.role not in {
        UserRole.super_admin,
        UserRole.admin,
        UserRole.hod,
    }:
        raise _forbidden(
            "ENROLLMENT_PERMISSION_DENIED",
            "You do not have permission to enroll students.",
        )

    # HOD may only operate within their assigned department.
    if current_user.role == UserRole.hod:
        from app.modules.user_scope.repository import get_assignment

        assignment = await get_assignment(
            db,
            tenant_id,
            current_user.id,
            college_id,
            course.department_id,
        )

        if assignment is None:
            raise _forbidden(
                "DEPARTMENT_ACCESS_DENIED",
                "You do not have access to this course department.",
            )

    existing = await repository.get_enrollment(
        db,
        tenant_id,
        college_id,
        course_id,
        student_id,
    )

    if existing is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "code": "ENROLLMENT_EXISTS",
                "message": "Student is already enrolled in this course.",
            },
        )

    return await repository.create_enrollment(
        db,
        tenant_id,
        college_id,
        course_id,
        student_id,
    )

async def create_attendance_session(
    db: AsyncSession,
    *,
    current_user: User,
    tenant_id: uuid.UUID,
    college_id: uuid.UUID,
    course_id: uuid.UUID,
    held_on: date,
    period: int,
) -> AttendanceSession:

    course_result = await db.execute(
        select(Course).where(
            Course.id == course_id,
            Course.tenant_id == tenant_id,
            Course.college_id == college_id,
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

    if course.faculty_id is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "code": "COURSE_FACULTY_NOT_ASSIGNED",
                "message": "A faculty member must be assigned to the course before attendance can be taken.",
            },
        )

    if current_user.role == UserRole.faculty:
        if course.faculty_id != current_user.id:
            raise _forbidden(
                "COURSE_ACCESS_DENIED",
                "You are not assigned to this course.",
            )

    if current_user.role == UserRole.hod:
        from app.modules.user_scope.repository import get_assignment

        assignment = await get_assignment(
            db,
            tenant_id,
            current_user.id,
            college_id,
            course.department_id,
        )

        if assignment is None:
            raise _forbidden(
                "DEPARTMENT_ACCESS_DENIED",
                "You do not have access to this course department.",
            )

    if current_user.role not in {
        UserRole.super_admin,
        UserRole.admin,
        UserRole.hod,
        UserRole.faculty,
    }:
        raise _forbidden(
            "ATTENDANCE_PERMISSION_DENIED",
            "You do not have permission to create attendance sessions.",
        )

    return await repository.create_session(
        db,
        tenant_id,
        college_id,
        course_id,
        course.faculty_id,
        held_on,
        period,
    )

async def mark_attendance(
    db: AsyncSession,
    *,
    current_user: User,
    tenant_id: uuid.UUID,
    college_id: uuid.UUID,
    session_id: uuid.UUID,
    records: list[tuple[uuid.UUID, str]],
) -> list[AttendanceRecord]:

    session = await repository.get_session(
        db,
        tenant_id,
        college_id,
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

    if current_user.role == UserRole.faculty:
        if session.faculty_id != current_user.id:
            raise _forbidden(
                "ATTENDANCE_SESSION_ACCESS_DENIED",
                "You do not have access to this attendance session.",
            )

    elif current_user.role == UserRole.hod:
        course_result = await db.execute(
            select(Course).where(
                Course.id == session.course_id,
                Course.tenant_id == tenant_id,
                Course.college_id == college_id,
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

        from app.modules.user_scope.repository import get_assignment

        assignment = await get_assignment(
            db,
            tenant_id,
            current_user.id,
            college_id,
            course.department_id,
        )

        if assignment is None:
            raise _forbidden(
                "DEPARTMENT_ACCESS_DENIED",
                "You do not have access to this attendance session.",
            )

    elif current_user.role not in {
        UserRole.super_admin,
        UserRole.admin,
    }:
        raise _forbidden(
            "ATTENDANCE_PERMISSION_DENIED",
            "You do not have permission to mark attendance.",
        )

    enrollment_result = await db.execute(
        select(CourseEnrollment).where(
            CourseEnrollment.tenant_id == tenant_id,
            CourseEnrollment.college_id == college_id,
            CourseEnrollment.course_id == session.course_id,
        )
    )

    enrolled = {
        row.student_id
        for row in enrollment_result.scalars().all()
    }

    submitted_ids = {student_id for student_id, _ in records}

    not_enrolled = submitted_ids - enrolled

    if not_enrolled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "code": "STUDENT_NOT_ENROLLED",
                "message": "One or more students are not enrolled in this course.",
                "student_ids": [
                    str(student_id)
                    for student_id in not_enrolled
                ],
            },
        )

    result_records: list[AttendanceRecord] = []

    for student_id, status_value in records:
        existing = await repository.get_record(
            db,
            tenant_id,
            college_id,
            session_id,
            student_id,
        )

        if existing is None:
            record = await repository.create_record(
                db,
                tenant_id,
                college_id,
                session_id,
                student_id,
                status_value,
            )
        else:
            record = await repository.update_record_status(
                db,
                existing,
                status_value,
            )

        result_records.append(record)

    await db.flush()

    return result_records

async def get_student_summary(
    db: AsyncSession,
    *,
    current_user: User,
    tenant_id: uuid.UUID,
    college_id: uuid.UUID,
    student_id: uuid.UUID | None,
) -> dict:

    resolved_student_id = student_id

    if current_user.role == UserRole.student:
        student_result = await db.execute(
            select(Student).where(
                Student.user_id == current_user.id,
                Student.tenant_id == tenant_id,
                Student.college_id == college_id,
            )
        )

        student = student_result.scalar_one_or_none()

        if student is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "code": "STUDENT_PROFILE_NOT_FOUND",
                    "message": "Student profile not found.",
                },
            )

        resolved_student_id = student.id

    if resolved_student_id is None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "code": "STUDENT_ID_REQUIRED",
                "message": "student_id is required for this role.",
            },
        )

    student_result = await db.execute(
        select(Student).where(
            Student.id == resolved_student_id,
            Student.tenant_id == tenant_id,
            Student.college_id == college_id,
        )
    )

    student = student_result.scalar_one_or_none()

    if student is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "STUDENT_NOT_FOUND",
                "message": "Student not found in this college.",
            },
        )

    records = await repository.list_student_records(
        db,
        tenant_id,
        college_id,
        resolved_student_id,
    )

    total = len(records)
    present = sum(1 for r in records if r.status == "present")
    absent = sum(1 for r in records if r.status == "absent")
    late = sum(1 for r in records if r.status == "late")
    excused = sum(1 for r in records if r.status == "excused")

    percentage = (
        ((present + late) / total) * 100
        if total
        else 0.0
    )

    return {
        "student_id": resolved_student_id,
        "total_sessions": total,
        "present": present,
        "absent": absent,
        "late": late,
        "excused": excused,
        "percentage": round(percentage, 2),
    }

async def remove_enrollment(
    db: AsyncSession,
    *,
    current_user: User,
    tenant_id: uuid.UUID,
    college_id: uuid.UUID,
    enrollment_id: uuid.UUID,
) -> None:
    if current_user.role not in {
        UserRole.super_admin,
        UserRole.admin,
        UserRole.hod,
    }:
        raise _forbidden(
            "ENROLLMENT_PERMISSION_DENIED",
            "You do not have permission to remove enrollments.",
        )

    enrollment = await repository.get_enrollment_by_id(
        db,
        tenant_id,
        college_id,
        enrollment_id,
    )

    if enrollment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "code": "ENROLLMENT_NOT_FOUND",
                "message": "Enrollment not found.",
            },
        )

    if current_user.role == UserRole.hod:
        course_result = await db.execute(
            select(Course).where(
                Course.id == enrollment.course_id,
                Course.tenant_id == tenant_id,
                Course.college_id == college_id,
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

        from app.modules.user_scope.repository import get_assignment

        assignment = await get_assignment(
            db,
            tenant_id,
            current_user.id,
            college_id,
            course.department_id,
        )

        if assignment is None:
            raise _forbidden(
                "DEPARTMENT_ACCESS_DENIED",
                "You do not have access to this course department.",
            )

    await repository.delete_enrollment(
        db,
        enrollment,
    )