import uuid
from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field

from app.db.models import ReviewStatus


class Account(BaseModel):
    name: str = Field(..., min_length=1, description="Имя студента")


class Actor(BaseModel):
    account: Account


class Verb(BaseModel):
    id: str = Field(..., min_length=1, description="URL, действие")


class Definition(BaseModel):
    type: str = Field(..., min_length=1, description="Тип объекта")


class ObjectBase(BaseModel):
    id: str = Field(..., min_length=1, description="Ссылка на артефакт (URL)")
    definition: Definition


class XAPIStatement(BaseModel):
    """
    Главная схема запроса
    """

    actor: Actor
    verb: Verb
    object: ObjectBase
    context: Optional[Dict[str, Any]] = None
    timestamp: datetime


class EvidenceResponce(BaseModel):
    """
    Схема для отдачи данных из базы данных - наружу.
    """

    id: uuid.UUID
    actor_id: str
    verb_id: str
    object_id: str
    timestamp: datetime
    source_system: str
    source_type: str
    context_id: str
    note: Optional[str] = None
    raw_data: Optional[Dict[str, Any]] = None
    review_status: ReviewStatus
    reviewed_by: str
    stored: datetime

    class Config:
        # Эта настройка говорит Pydantic, что данные будут приходить
        # не как словари, а как ORM-объекты SQLAlchemy.
        from_attributes = True
