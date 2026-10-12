
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_create_task():
    response = client.post(
        "/tasks",
        json={
            "title": "Write automated tests",
            "description": "Test the API",
            "priority": "high",
        },
    )

    assert response.status_code == 201
    assert response.json()["title"] == "Write automated tests"
    assert response.json()["completed"] is False


def test_invalid_priority():
    response = client.post(
        "/tasks",
        json={"title": "Invalid task", "priority": "urgent"},
    )

    assert response.status_code == 422
