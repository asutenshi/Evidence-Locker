import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class EvindenceRecord(Base):
    __tablename__ = "evidence_records"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    actor_id: Mapped[str] = mapped_column(String, index=True)
    source_system: Mapped[str] = mapped_column(String)
    source_type: Mapped[str] = mapped_column(String)
    evidence_link: Mapped[str] = mapped_column(String)
    context: Mapped[str] = mapped_column(String)
    timestamp: Mapped[datetime] = mapped_column(DateTime)
    # Статус может быть draft, pending, reviewed, rejected
    review_status: Mapped[str] = mapped_column(String, default="pending")
    reviewed_by: Mapped[str] = mapped_column(String, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )

    competencies = relationship("EvidenceCompetency", back_populates="evidence")


class EvidenceCompetency(Base):
    __tablename__ = "evidence_competencies"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    evidence_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("evidence_records.id"))
    competency_id: Mapped[str] = mapped_column(String, index=True)
    proposed_by: Mapped[str] = mapped_column(String)

    evidence = relationship("EvidenceRecord", back_populates="competencies")
