import uuid
from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field


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
    context = Optional[Dict[str, Any]] = None
    timestamp = datetime


class EvidenceResponce(BaseModel):
    """
    Схема для отдачи данных из базы данных - наружу.
    """

    id: uuid.UUID
    actor_id: str
    source_system: str
    source_type: str
    evidence_link: str
    context: Optional[str] = None
    timestamp: datetime
    review_status: str
    reviewed_by: str
    created_at: datetime

    class Config:
        # Эта настройка говорит Pydantic, что данные будут приходить
        # не как словари, а как ORM-объекты SQLAlchemy.
        from_attributes = True
