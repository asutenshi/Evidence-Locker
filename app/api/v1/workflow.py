from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.db.models import EvidenceCompetency, EvidenceRecord
from app.schemas.evidence import EvidenceResponse

router = APIRouter(prefix="/api/v1", tags=["Workflow"])


@router.get("/evidences", response_model=list[EvidenceResponse])
def get_evidences(
    actor_id: Optional[str] = Query(None, description="Фильтр по ID студента"),
    verb_id: Optional[str] = Query(None, description="Фильтр по URI глагола"),
    object_id: Optional[str] = Query(None, description="Фильтр по URI объекта"),
    competency_id: Optional[str] = Query(None, description="Фильтр по ID компетенции"),
    review_status: Optional[str] = Query(
        None, description="Фильтр по статусу (pending/reviewed)"
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
