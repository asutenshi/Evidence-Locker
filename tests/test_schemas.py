import uuid
from datetime import datetime, timezone

import pytest
from pydantic import ValidationError

from app.schemas.evidence import XAPIStatement


def test_xapi_statement_valid():
    data = {
        "id": str(uuid.uuid4()),
        "actor": {"account": {"name": "Ivan Ivanov"}},
        "verb": {"id": "http://adlnet.gov/expapi/verbs/completed"},
        "object": {
            "id": "http://example.com/activities/course-1",
            "definition": {"type": "http://adlnet.gov/expapi/activities/course"},
        },
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "context": {
            "extensions": {"source_system": "lms_alpha", "source_type": "moodle"}
        },
    }

    statement = XAPIStatement(**data)
    assert statement.actor_id == "Ivan Ivanov"
    assert statement.source_system == "lms_alpha"
    assert statement.source_type == "moodle"


def test_xapi_statement_missing_source_system():
    data = {
        "id": str(uuid.uuid4()),
        "actor": {"account": {"name": "Ivan Ivanov"}},
        "verb": {"id": "http://adlnet.gov/expapi/verbs/completed"},
        "object": {
            "id": "http://example.com/activities/course-1",
            "definition": {"type": "http://adlnet.gov/expapi/activities/course"},
        },
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "context": {"extensions": {"source_type": "moodle"}},
    }

    with pytest.raises(ValidationError) as exc_info:
        XAPIStatement(**data)

    assert "Обязательное поле 'source_system' отсутствует" in str(exc_info.value)


def test_xapi_statement_missing_source_type():
    data = {
        "id": str(uuid.uuid4()),
        "actor": {"account": {"name": "Ivan Ivanov"}},
        "verb": {"id": "http://adlnet.gov/expapi/verbs/completed"},
        "object": {
            "id": "http://example.com/activities/course-1",
            "definition": {"type": "http://adlnet.gov/expapi/activities/course"},
        },
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "context": {"extensions": {"source_system": "lms_alpha"}},
    }

    with pytest.raises(ValidationError) as exc_info:
        XAPIStatement(**data)

    assert "Обязательное поле 'source_type' отсутствует" in str(exc_info.value)


def test_xapi_statement_invalid_actor():
    data = {
        "id": str(uuid.uuid4()),
        "actor": {},  # No identifiers
        "verb": {"id": "http://adlnet.gov/expapi/verbs/completed"},
        "object": {
            "id": "http://example.com/activities/course-1",
            "definition": {"type": "http://adlnet.gov/expapi/activities/course"},
        },
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "context": {
            "extensions": {"source_system": "lms_alpha", "source_type": "moodle"}
        },
    }

    with pytest.raises(ValidationError) as exc_info:
        XAPIStatement(**data)

    assert "Actor должен содержать хотя бы один валидный идентификатор" in str(
        exc_info.value
    )


def test_xapi_statement_missing_definition():
    data = {
        "id": str(uuid.uuid4()),
        "actor": {"account": {"name": "Ivan Ivanov"}},
        "verb": {"id": "http://adlnet.gov/expapi/verbs/completed"},
        "object": {"id": "http://github.com/my-org/my-repo/commit/abc1234"},
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "context": {
            "extensions": {"source_system": "lms_alpha", "source_type": "moodle"}
        },
    }

    statement = XAPIStatement(**data)
    assert statement.actor_id == "Ivan Ivanov"
    assert statement.object.definition is None


def test_xapi_statement_missing_timestamp():
    data = {
        "id": str(uuid.uuid4()),
        "actor": {"account": {"name": "Ivan Ivanov"}},
        "verb": {"id": "http://adlnet.gov/expapi/verbs/completed"},
        "object": {"id": "http://github.com/my-org/my-repo/commit/abc1234"},
        "context": {
            "extensions": {"source_system": "lms_alpha", "source_type": "moodle"}
        },
    }

    statement = XAPIStatement(**data)
    assert statement.timestamp is not None
    assert isinstance(statement.timestamp, datetime)

