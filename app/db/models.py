import uuid
import enum
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String, Text, JSON, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class ReviewStatus(str, enum.Enum):
    draft = "draft"
    pending = "pending"
    reviewed = "reviewed"
    rejected = "rejected"

class CompetencyStatus(str, enum.Enum):
    pending = "pending"
    approved = "approved"
    rejected = "rejected"
    unlinked = "unlinked"

class EvidenceRecord(Base):
    __tablename__ = "evidence_records"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    actor_id: Mapped[str] = mapped_column(String, index=True)
    verb_id: Mapped[str] = mapped_column(String)
    object_id: Mapped[str] = mapped_column(String)
    timestamp: Mapped[datetime] = mapped_column(DateTime)
    source_system: Mapped[str] = mapped_column(String)
    source_type: Mapped[str] = mapped_column(String)
    context_id: Mapped[str] = mapped_column(String)
    note: Mapped[str | None] = mapped_column(Text, nullable=True)
    raw_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    review_status: Mapped[ReviewStatus] = mapped_column(
        SQLEnum(ReviewStatus), default=ReviewStatus.pending
    )
    reviewed_by: Mapped[str] = mapped_column(String, default="0")
    stored: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
    competencies = relationship("EvidenceCompetency", back_populates="evidence")


class EvidenceCompetency(Base):
    __tablename__ = "evidence_competencies"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    evidence_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("evidence_records.id"))
    competency_id: Mapped[str] = mapped_column(String, index=True)
    proposed_by: Mapped[str] = mapped_column(String)
    status: Mapped[CompetencyStatus] = mapped_column(
        SQLEnum(CompetencyStatus), default=CompetencyStatus.pending
    )
    reviewed_by: Mapped[str | None] = mapped_column(String, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, 
        default=lambda: datetime.now(timezone.utc), 
        onupdate=lambda: datetime.now(timezone.utc)
    )
    evidence = relationship("EvidenceRecord", back_populates="competencies")
