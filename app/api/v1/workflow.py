from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.db.models import EvidenceCompetency, EvidenceRecord
from app.schemas.evidence import EvidenceResponce

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
