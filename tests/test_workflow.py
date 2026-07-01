import uuid
from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.api.dependencies import (
    get_collector_token,
    get_db,
    get_student_token,
    get_teacher_token,
)
from app.db.database import Base
from app.main import app

SQLALCHEMY_DATABASE_URL = "sqlite:///./data/test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def setup_database():
    """Создает чистые таблицы перед каждым тестом и удаляет после."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


client = TestClient(app)


@pytest.fixture
def teacher_headers():
    return {"Authorization": f"Bearer {get_teacher_token()}"}


@pytest.fixture
def collector_headers():
    return {"Authorization": f"Bearer {get_collector_token()}"}


@pytest.fixture
def student_headers():
    return {"Authorization": f"Bearer {get_student_token()}"}


@pytest.fixture
def test_evidence_id(collector_headers):
    """Вспомогательная фикстура: создает тестовое свидетельство в БД."""
    payload = {
        "id": str(uuid.uuid4()),
        "actor": {"account": {"name": "test_student"}},
        "verb": {"id": "http://example.com/verb/tested"},
        "object": {
            "id": "http://example.com/object/test",
            "definition": {"type": "unit-test"},
        },
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }
    response = client.post("/api/v1/evidences", json=payload, headers=collector_headers)
    assert response.status_code == 201
    return response.json()["id"]


# ТЕСТЫ GET /evidences


def test_get_evidences_unauthorized():
    response = client.get("/api/v1/evidences")
    assert response.status_code == 401


def test_get_evidences_wrong_token():
    headers = {"Authorization": "Bearer hacker_token"}
    response = client.get("/api/v1/evidences", headers=headers)
    assert response.status_code == 403


def test_get_evidences_authorized(teacher_headers):
    response = client.get("/api/v1/evidences", headers=teacher_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_evidences_with_filtration(teacher_headers, test_evidence_id):
    response = client.get(
        "/api/v1/evidences?review_status=pending", headers=teacher_headers
    )

    assert response.status_code == 200
    data = response.json()

    assert any(ev["id"] == test_evidence_id for ev in data)

    response_empty = client.get(
        "/api/v1/evidences?review_status=rejected", headers=teacher_headers
    )
    assert not any(ev["id"] == test_evidence_id for ev in response_empty.json())


# ТЕСТЫ PATCH /review


def test_patch_review_auth_and_logic(
    teacher_headers, collector_headers, test_evidence_id
):
    # 1. Без токена -> 401
    res1 = client.patch(
        f"/api/v1/evidences/{test_evidence_id}/review",
        json={"status": "reviewed"},
    )
    assert res1.status_code == 401

    # 2. Неверная роль (Сборщик пытается заревьюить) -> 403
    res2 = client.patch(
        f"/api/v1/evidences/{test_evidence_id}/review",
        json={"status": "reviewed"},
        headers=collector_headers,
    )
    assert res2.status_code == 403

    # 3. Успешная смена статуса (Преподаватель) -> 200
    res3 = client.patch(
        f"/api/v1/evidences/{test_evidence_id}/review",
        json={"status": "reviewed", "note": "All good"},
        headers=teacher_headers,
    )
    assert res3.status_code == 200
    assert res3.json()["review_status"] == "reviewed"


# ТЕСТЫ POST /competencies


def test_post_competencies_auth_and_logic(
    teacher_headers, collector_headers, student_headers, test_evidence_id
):
    payload = {"competency_id": "teamwork_101"}

    # 1. Без токена -> 401
    res1 = client.post(
        f"/api/v1/evidences/{test_evidence_id}/competencies", json=payload
    )
    assert res1.status_code == 401

    # 2. Неверная роль (Студент) -> 403
    res2 = client.post(
        f"/api/v1/evidences/{test_evidence_id}/competencies",
        json=payload,
        headers=student_headers,
    )
    assert res2.status_code == 403

    # 3. Успешно (Сборщик) -> статус связи должен быть pending
    res3 = client.post(
        f"/api/v1/evidences/{test_evidence_id}/competencies",
        json=payload,
        headers=collector_headers,
    )
    assert res3.status_code == 201
    assert res3.json()["proposed_by"] == "collector"
    assert res3.json()["status"] == "pending"

    # 4. Успешно (Преподаватель) -> статус связи должен быть approved
    res4 = client.post(
        f"/api/v1/evidences/{test_evidence_id}/competencies",
        json={"competency_id": "leadership"},
        headers=teacher_headers,
    )
    assert res4.status_code == 201
    assert res4.json()["proposed_by"] == "teacher"
    assert res4.json()["status"] == "approved"
