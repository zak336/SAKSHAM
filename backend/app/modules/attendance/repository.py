import uuid

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.attendance.models import (
    AttendanceRecord,
    AttendanceSession,
    CourseEnrollment,
)


async def get_enrollment(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    college_id: uuid.UUID,
    course_id: uuid.UUID,
    student_id: uuid.UUID,
) -> CourseEnrollment | None:
    result = await db.execute(
        select(CourseEnrollment).where(
            CourseEnrollment.tenant_id == tenant_id,
            CourseEnrollment.college_id == college_id,
            CourseEnrollment.course_id == course_id,
            CourseEnrollment.student_id == student_id,
        )
    )
    return result.scalar_one_or_none()


async def create_enrollment(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    college_id: uuid.UUID,
    course_id: uuid.UUID,
    student_id: uuid.UUID,
) -> CourseEnrollment:
    enrollment = CourseEnrollment(
        tenant_id=tenant_id,
        college_id=college_id,
        course_id=course_id,
        student_id=student_id,
    )
    db.add(enrollment)
    await db.flush()
    return enrollment


async def list_enrollments(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    college_id: uuid.UUID,
    course_id: uuid.UUID | None = None,
    student_id: uuid.UUID | None = None,
) -> list[CourseEnrollment]:
    query = select(CourseEnrollment).where(
        CourseEnrollment.tenant_id == tenant_id,
        CourseEnrollment.college_id == college_id,
    )

    if course_id is not None:
        query = query.where(
            CourseEnrollment.course_id == course_id
        )

    if student_id is not None:
        query = query.where(
            CourseEnrollment.student_id == student_id
        )

    result = await db.execute(
        query.order_by(CourseEnrollment.created_at)
    )

    return list(result.scalars().all())


async def get_session(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    college_id: uuid.UUID,
    session_id: uuid.UUID,
) -> AttendanceSession | None:
    result = await db.execute(
        select(AttendanceSession).where(
            AttendanceSession.id == session_id,
            AttendanceSession.tenant_id == tenant_id,
            AttendanceSession.college_id == college_id,
        )
    )
    return result.scalar_one_or_none()


async def create_session(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    college_id: uuid.UUID,
    course_id: uuid.UUID,
    faculty_id: uuid.UUID,
    held_on,
    period: int,
) -> AttendanceSession:
    session = AttendanceSession(
        tenant_id=tenant_id,
        college_id=college_id,
        course_id=course_id,
        faculty_id=faculty_id,
        held_on=held_on,
        period=period,
    )
    db.add(session)
    await db.flush()
    return session


async def create_record(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    college_id: uuid.UUID,
    session_id: uuid.UUID,
    student_id: uuid.UUID,
    status: str,
) -> AttendanceRecord:
    record = AttendanceRecord(
        tenant_id=tenant_id,
        college_id=college_id,
        session_id=session_id,
        student_id=student_id,
        status=status,
    )
    db.add(record)
    await db.flush()
    return record

async def get_record(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    college_id: uuid.UUID,
    session_id: uuid.UUID,
    student_id: uuid.UUID,
) -> AttendanceRecord | None:
    result = await db.execute(
        select(AttendanceRecord).where(
            AttendanceRecord.tenant_id == tenant_id,
            AttendanceRecord.college_id == college_id,
            AttendanceRecord.session_id == session_id,
            AttendanceRecord.student_id == student_id,
        )
    )
    return result.scalar_one_or_none()


async def list_session_records(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    college_id: uuid.UUID,
    session_id: uuid.UUID,
) -> list[AttendanceRecord]:
    result = await db.execute(
        select(AttendanceRecord)
        .where(
            AttendanceRecord.tenant_id == tenant_id,
            AttendanceRecord.college_id == college_id,
            AttendanceRecord.session_id == session_id,
        )
        .order_by(AttendanceRecord.student_id)
    )

    return list(result.scalars().all())


async def list_student_records(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    college_id: uuid.UUID,
    student_id: uuid.UUID,
) -> list[AttendanceRecord]:
    result = await db.execute(
        select(AttendanceRecord)
        .where(
            AttendanceRecord.tenant_id == tenant_id,
            AttendanceRecord.college_id == college_id,
            AttendanceRecord.student_id == student_id,
        )
        .order_by(AttendanceRecord.marked_at)
    )

    return list(result.scalars().all())


async def update_record_status(
    db: AsyncSession,
    record: AttendanceRecord,
    status: str,
) -> AttendanceRecord:
    record.status = status
    await db.flush()
    return record

async def list_sessions(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    college_id: uuid.UUID,
    course_id: uuid.UUID | None = None,
) -> list[AttendanceSession]:
    query = select(AttendanceSession).where(
        AttendanceSession.tenant_id == tenant_id,
        AttendanceSession.college_id == college_id,
    )

    if course_id is not None:
        query = query.where(
            AttendanceSession.course_id == course_id
        )

    result = await db.execute(
        query.order_by(
            AttendanceSession.held_on.desc(),
            AttendanceSession.period.desc(),
        )
    )

    return list(result.scalars().all())

async def get_enrollment_by_id(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    college_id: uuid.UUID,
    enrollment_id: uuid.UUID,
) -> CourseEnrollment | None:
    result = await db.execute(
        select(CourseEnrollment).where(
            CourseEnrollment.id == enrollment_id,
            CourseEnrollment.tenant_id == tenant_id,
            CourseEnrollment.college_id == college_id,
        )
    )
    return result.scalar_one_or_none()


async def delete_enrollment(
    db: AsyncSession,
    enrollment: CourseEnrollment,
) -> None:
    await db.delete(enrollment)
    await db.flush()

async def list_course_enrollments(
    db: AsyncSession,
    tenant_id: uuid.UUID,
    college_id: uuid.UUID,
    course_id: uuid.UUID,
) -> list[CourseEnrollment]:
    result = await db.execute(
        select(CourseEnrollment).where(
            CourseEnrollment.tenant_id == tenant_id,
            CourseEnrollment.college_id == college_id,
            CourseEnrollment.course_id == course_id,
        ).order_by(CourseEnrollment.created_at)
    )

    return list(result.scalars().all())