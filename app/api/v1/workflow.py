import json
import logging
import sys
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.db.models import EvidenceCompetency, EvidenceRecord, ReviewStatus
from app.schemas.evidence import EvidenceResponse

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
