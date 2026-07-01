import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.api.dependencies import get_teacher_token

client = TestClient(app)


@pytest.fixture
def teacher_headers():
    token = get_teacher_token()
    return {"Authorization": f"Bearer {token}"}


def test_get_evidences_unauthorized():
    """Тест: получение списка вообще без токена должно возвращать ошибку 401"""
    response = client.get("/api/v1/evidences")
    assert response.status_code == 401


def test_get_evidences_wrong_token():
    """Тест: получение списка с неверным токеном должно возвращать ошибку 403"""
    response = client.get(
        "/api/v1/evidences", headers={"Authorization": "Bearer fake_hacker_token"}
    )
    assert response.status_code == 403


def test_get_evidences_authorized(teacher_headers):
    """Тест: получение списка с токеном преподавателя должно работать 200"""
    response = client.get("/api/v1/evidences", headers=teacher_headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)
