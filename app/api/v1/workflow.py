import json
import logging
import sys
import uuid
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies import (
    get_db,
    verify_teacher_or_collector_token,
    verify_teacher_token,
)
from app.db.models import (
    CompetencyStatus,
    EvidenceCompetency,
    EvidenceRecord,
    ReviewStatus,
)
from app.schemas.evidence import (
    CompetencyLinkRequest,
    CompetencyLinkResponse,
    EvidenceResponse,
    ReviewRequest,
)

logger = logging.getLogger("evidence_locker")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter("%(message)s"))
if not logger.handlers:
    logger.addHandler(handler)

router = APIRouter(prefix="/api/v1", tags=["Workflow"])


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
    _token: str = Depends(verify_teacher_token),
    db: Session = Depends(get_db),
):
    """Получение списка свидетельств с возможностью фильтрации."""
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
        query = (
            query.join(EvidenceCompetency)
            .filter(
                EvidenceCompetency.competency_id == competency_id,
                EvidenceCompetency.status.in_(
                    [CompetencyStatus.approved, CompetencyStatus.pending]
                ),
            )
            .distinct()
        )

    return query.all()


@router.patch("/evidences/{evidence_id}/review", response_model=EvidenceResponse)
def review_evidence(
    evidence_id: uuid.UUID,
    payload: ReviewRequest,
    _token: str = Depends(verify_teacher_token),
    db: Session = Depends(get_db),
):
    """Изменение статуса свидетельства (ревью преподавателем)."""
    evidence = db.query(EvidenceRecord).filter(EvidenceRecord.id == evidence_id).first()
    if not evidence:
        raise HTTPException(status_code=404, detail="Свидетельство не найдено")

    evidence.review_status = payload.status
    evidence.reviewed_by = "0"

    if payload.note is not None:
        if payload.note.strip() == "":
            evidence.note = None
        else:
            evidence.note = payload.note

    db.commit()
    db.refresh(evidence)

    event_name = (
        "evidence.reviewed"
        if evidence.review_status == ReviewStatus.reviewed
        else "evidence.rejected"
    )
    log_event = {
        "event": event_name,
        "evidence_id": str(evidence.id),
        "status": evidence.review_status.value,
    }
    logger.info(json.dumps(log_event, ensure_ascii=False))

    return evidence


@router.post(
    "/evidences/{evidence_id}/competencies",
    response_model=CompetencyLinkResponse,
    status_code=status.HTTP_201_CREATED,
)
def link_competency(
    evidence_id: uuid.UUID,
    payload: CompetencyLinkRequest,
    role: str = Depends(verify_teacher_or_collector_token),
    db: Session = Depends(get_db),
):
    """Привязка компетенции к свидетельству (сборщиком или преподавателем)."""
    evidence = db.query(EvidenceRecord).filter(EvidenceRecord.id == evidence_id).first()
    if not evidence:
        raise HTTPException(status_code=404, detail="Свидетельство не найдено")

    if role == "teacher":
        status_val = CompetencyStatus.approved
        proposed_by = "teacher"
        reviewed_by = "0"
    else:
        status_val = CompetencyStatus.pending
        proposed_by = "collector"
        reviewed_by = None

    link = EvidenceCompetency(
        evidence_id=evidence_id,
        competency_id=payload.competency_id,
        proposed_by=proposed_by,
        status=status_val,
        reviewed_by=reviewed_by,
    )
    db.add(link)
    db.commit()
    db.refresh(link)

    log_event = {
        "event": "evidence.linked",
        "evidence_id": str(evidence_id),
        "competency_id": payload.competency_id,
    }
    logger.info(json.dumps(log_event, ensure_ascii=False))

    return link
