import json
import logging
import sys
import uuid
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.db.models import EvidenceCompetency, EvidenceRecord
from app.schemas.evidence import EvidenceResponce, ReviewRequest

logger = logging.getLogger("evidence_locker")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
logger.addHandler(handler)

router = APIRouter(prefix="/api/v1", tags=["Workflow"])


@router.get("/evidences", response_model=list[EvidenceResponce])
def get_evidences(
    actor_id: Optional[str] = Query(None, description="Фильтр по ID студента"),
    review_status: Optional[str] = Query(None, description="Фильтр по статусу: pending, reviewed, rejected"),
    context: Optional[str] = Query(None, description="Фильтр по контексту (проект/репозиторий)"),
    competency_id: Optional[str] = Query(None, description="Фильтр по ID компетенции"),
    db: Session = Depends(get_db),
):
    """
    Получение списка свидетельств с возможностью фильтрации.
    """
    query = db.query(EvidenceRecord)

    if actor_id:
        query = query.filter(EvidenceRecord.actor_id == actor_id)

    if review_status:
        query = query.filter(EvidenceRecord.review_status == review_status)

    if context:
        query = query.filter(EvidenceRecord.context.contains(context))

    if competency_id:
        query = query.join(EvidenceCompetency).filter(
            EvidenceCompetency.competency_id == competency_id
        )

    results = query.all()
    return results


@router.patch("/evidences/{evidence_id}/review")
def review_evidence(
    evidence_id: uuid.UUID,
    body: ReviewRequest,
    db: Session = Depends(get_db),
):
    """
    Смена статуса свидетельства (например, pending -> reviewed).
    Логирует событие evidence.reviewed в stdout (JSON Lines).
    """
    record = db.query(EvidenceRecord).filter(
        EvidenceRecord.id == evidence_id
    ).first()

    if not record:
        raise HTTPException(status_code=404, detail="Evidence not found")

    record.review_status = body.status
    record.reviewed_by = "0"  # По ТЗ: в MVP всегда "0"
    db.commit()
    db.refresh(record)

    # Event Emission — логирование события в stdout (JSON Lines)
    event = {
        "event": f"evidence.{body.status}",
        "evidence_id": str(record.id),
        "actor_id": record.actor_id,
        "new_status": body.status,
        "reviewed_by": record.reviewed_by,
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    logger.info(json.dumps(event, ensure_ascii=False))

    return {"status": "ok", "evidence_id": str(record.id), "new_status": body.status}
