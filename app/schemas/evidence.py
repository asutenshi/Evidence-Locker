import uuid
from datetime import datetime
from typing import Any, Dict, Optional

from pydantic import BaseModel, Field, model_validator

from app.db.models import ReviewStatus


class Account(BaseModel):
    name: str = Field(..., min_length=1, description="Имя студента")


class Actor(BaseModel):
    account: Optional[Account] = None
    mbox: Optional[str] = None
    mbox_sha1sum: Optional[str] = None
    openid: Optional[str] = None

    actor_id: str = Field(default="", description="Нормализованный ID пользователя")

    @model_validator(mode="after")
    def normalize_actor_id(self) -> "Actor":
        identifiers = {
            "account": self.account.name if self.account else None,
            "mbox": self.mbox,
            "mbox_sha1sum": self.mbox_sha1sum,
            "openid": self.openid,
        }

        valid_ids = {k: v for k, v in identifiers.items() if v is not None}

        if not valid_ids:
            raise ValueError(
                "Actor должен содержать хотя бы один валидный "
                "идентификатор (account, mbox, mbox_sha1sum, openid)"
            )

        self.actor_id = list(valid_ids.values())[0]
        return self


class Verb(BaseModel):
    id: str = Field(..., min_length=1, description="URL, действие")


class Definition(BaseModel):
    type: str = Field(..., min_length=1, description="Тип объекта")


class ObjectBase(BaseModel):
    id: str = Field(..., min_length=1, description="Ссылка на артефакт (URL)")
    definition: Definition


class XAPIStatement(BaseModel):
    actor: Actor
    verb: Verb
    object: ObjectBase
    context: Optional[Dict[str, Any]] = None
    timestamp: datetime

    actor_id: str = Field(default="")
    source_system: str = Field(default="")
    source_type: str = Field(default="")
    context_id: str = Field(default="")

    @model_validator(mode="after")
    def extract_business_fields(self) -> "XAPIStatement":
        self.actor_id = self.actor.actor_id

        ctx = self.context or {}
        extensions = ctx.get("extensions", {})

        self.source_system = extensions.get("source_system", "unknown_system")
        self.source_type = extensions.get("source_type", self.object.definition.type)

        self.context_id = ctx.get("context_id", ctx.get("project", "default_context"))

        return self


class EvidenceResponse(BaseModel):
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
        from_attributes = True


class ReviewRequest(BaseModel):
    """
    Схема входящего запроса на смену статуса свидетельства.
    """

    status: str = Field(
        ...,
        description="Новый статус: reviewed или rejected",
    )
    note: Optional[str] = Field(
        None,
        description="Комментарий преподавателя (опционально)",
    )
