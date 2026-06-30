import json
import sys

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.db.database import SessionLocal
from app.db.models import EvidenceRecord, ReviewStatus
from app.schemas.evidence import EvidenceResponse, XAPIStatement

router = APIRouter(prefix="/api/v1", tags=["Ingestion"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close


@router.post(
    "/evidences",
    response_model=EvidenceResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Прием xAPI Statement",
)
def ingest_evidence(statement: XAPIStatement, db: Session = Depends(get_db)):
    ctx = statement.context or {}
    extensions = ctx.get("extensions", {})
    note = extensions.get("note")

    db_record = EvidenceRecord(
        id=statement.id,
        actor_id=statement.actor_id,
        verb_id=statement.verb.id,
        object_id=statement.object.id,
        timestamp=statement.timestamp,
        source_system=statement.source_system,
        source_type=statement.source_type,
        context_id=statement.context_id,
        note=note,
        raw_data=statement.model_dump(mode="json"),
        review_status=ReviewStatus.pending,
        reviewed_by="0",
    )

    db.add(db_record)
    db.commit()
    db.refresh(db_record)

    log_event = {
        "event": "evidence.created",
        "evidence_id": str(db_record.id),
        "actor_id": db_record.actor_id,
        "source_system": db_record.source_system,
    }

    sys.stdout.write(json.dumps(log_event) + "\n")
    sys.stdout.flush()

    return db_record
