import uuid
from datetime import datetime

from app.api.dependencies import get_collector_token, get_teacher_token


def test_ingest_evidence_valid(client):
    token = get_collector_token()
    statement_id = str(uuid.uuid4())
    data = {
        "id": statement_id,
        "actor": {"account": {"name": "Ivan Ivanov"}},
        "verb": {"id": "http://adlnet.gov/expapi/verbs/completed"},
        "object": {
            "id": "http://example.com/activities/course-1",
            "definition": {"type": "http://adlnet.gov/expapi/activities/course"},
        },
        "timestamp": datetime.utcnow().isoformat(),
        "context": {
            "extensions": {"source_system": "lms_alpha", "source_type": "moodle"}
        },
    }

    response = client.post(
        "/api/v1/evidences", json=data, headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 201
    resp_data = response.json()
    assert resp_data["id"] == statement_id
    assert resp_data["source_system"] == "lms_alpha"
    assert resp_data["source_type"] == "moodle"


def test_ingest_evidence_invalid_missing_fields(client):
    token = get_collector_token()
    statement_id = str(uuid.uuid4())
    data = {
        "id": statement_id,
        "actor": {"account": {"name": "Ivan Ivanov"}},
        "verb": {"id": "http://adlnet.gov/expapi/verbs/completed"},
        "object": {
            "id": "http://example.com/activities/course-1",
            "definition": {"type": "http://adlnet.gov/expapi/activities/course"},
        },
        "timestamp": datetime.utcnow().isoformat(),
        "context": {
            "extensions": {
                # missing source_system and source_type
            }
        },
    }

    response = client.post(
        "/api/v1/evidences", json=data, headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 422
    assert "source_system" in response.text


def test_ingest_evidence_unauthorized(client):
    data = {
        "id": str(uuid.uuid4()),
        "actor": {"account": {"name": "Ivan Ivanov"}},
        "verb": {"id": "http://adlnet.gov/expapi/verbs/completed"},
        "object": {
            "id": "http://example.com/activities/course-1",
            "definition": {"type": "http://adlnet.gov/expapi/activities/course"},
        },
        "timestamp": datetime.utcnow().isoformat(),
        "context": {
            "extensions": {"source_system": "lms_alpha", "source_type": "moodle"}
        },
    }

    # Missing auth header (HTTPBearer returns 401)
    response = client.post("/api/v1/evidences", json=data)
    assert response.status_code == 401

    # Invalid auth token
    response = client.post(
        "/api/v1/evidences",
        json=data,
        headers={"Authorization": "Bearer invalid_token"},
    )
    assert response.status_code == 403

    # Wrong role token
    teacher_token = get_teacher_token()
    response = client.post(
        "/api/v1/evidences",
        json=data,
        headers={"Authorization": f"Bearer {teacher_token}"},
    )
    assert response.status_code == 403
