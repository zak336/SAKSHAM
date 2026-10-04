"""User responsibility models for tracking Faculty, HOD, and other responsibilities."""

import enum
import uuid
from datetime import date, datetime

from sqlalchemy import Boolean, Date, ForeignKey, String, TIMESTAMP, UniqueConstraint, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class ResponsibilityType(str, enum.Enum):
    """Types of responsibilities a user can have."""
    faculty = "faculty"
    hod = "hod"
    # Future: librarian, sports_coordinator, etc.


class UserResponsibility(Base):
    """Tracks responsibilities assigned to users over time.
    
    A user may have multiple responsibilities simultaneously (e.g., Faculty + HOD).
    This table maintains historical records with effective dates.
    """
    __tablename__ = "user_responsibilities"
    
    __table_args__ = (
        # Prevent duplicate active responsibilities for same user
        UniqueConstraint(
            "tenant_id",
            "college_id", 
            "user_id",
            "responsibility",
            name="uq_user_responsibility_active",
            postgresql_where="is_active = true"
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )
    
    tenant_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tenants.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    college_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("colleges.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    
    responsibility: Mapped[ResponsibilityType] = mapped_column(
        String(50),
        nullable=False,
        index=True
    )
    
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default="true",
        index=True
    )
    
    starts_at: Mapped[date | None] = mapped_column(
        Date,
        nullable=True
    )
    
    ends_at: Mapped[date | None] = mapped_column(
        Date,
        nullable=True
    )
    
    assigned_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True
    )
    
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        nullable=False
    )
    
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

    def __repr__(self) -> str:
        return f"<UserResponsibility user_id={self.user_id!r} responsibility={self.responsibility} active={self.is_active}>"
