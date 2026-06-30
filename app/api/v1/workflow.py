import json
import logging
import sys
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.db.models import EvidenceCompetency, EvidenceRecord, ReviewStatus
from app.schemas.evidence import EvidenceResponse, ReviewRequest

router = APIRouter(prefix="/api/v1", tags=["Workflow"])

logger = logging.getLogger("evidence_locker")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter("%(message)s"))
if not logger.handlers:
    logger.addHandler(handler)


@router.get("/evidences", response_model=list[EvidenceResponse])
def get_evidences(
    actor_id: Optional[str] = Query(None, description="Фильтр по ID студента"),
    verb_id: Optional[str] = Query(None, description="Фильтр по URI глагола"),
    object_id: Optional[str] = Query(None, description="Фильтр по URI объекта"),
    competency_id: Optional[str] = Query(None, description="Фильтр по ID компетенции"),
    review_status: Optional[ReviewStatus] = Query(
        None, description="Фильтр по статусу"
    ),
    source_system: Optional[str] = Query(None, description="Фильтр по источнику"),
    context_id: Optional[str] = Query(None, description="Фильтр по ID контекста"),
    db: Session = Depends(get_db),
):
    """
    Получение списка свидетельств с возможностью фильтрации.
    """
    query = db.query(EvidenceRecord)

    if actor_id:
        query = query.filter(EvidenceRecord.actor_id == actor_id)
    if verb_id:
        query = query.filter(EvidenceRecord.verb_id == verb_id)
    if object_id:
        query = query.filter(EvidenceRecord.object_id == object_id)
    if review_status:
        query = query.filter(EvidenceRecord.review_status == review_status)
    if source_system:
        query = query.filter(EvidenceRecord.source_system == source_system)
    if context_id:
        query = query.filter(EvidenceRecord.context_id == context_id)
    if competency_id:
        query = query.join(EvidenceCompetency).filter(
            EvidenceCompetency.competency_id == competency_id
        )

    return query.all()


@router.patch("/evidences/{evidence_id}/review")
def review_evidence(
    evidence_id: uuid.UUID,
    payload: ReviewRequest,
    db: Session = Depends(get_db),
):
    """
    Изменение статуса свидетельства (ревью преподавателем).
    """
    record = db.query(EvidenceRecord).filter(EvidenceRecord.id == evidence_id).first()

    if not record:
        raise HTTPException(status_code=404, detail="Свидетельство не найдено")

    record.review_status = payload.status
    record.reviewed_by = "0"

    if payload.note is not None:
        record.note = payload.note

    db.commit()

    log_event = {
        "event": f"evidence.{payload.status.value}", 
        "evidence_id": str(record.id),
        "actor_id": record.actor_id,
        "note": record.note,
    }

    logger.info(json.dumps(log_event))

    return {"message": "Статус успешно обновлен", "status": payload.status}