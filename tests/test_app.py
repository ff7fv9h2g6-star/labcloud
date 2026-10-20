
import pytest
from app import app, requests_db


@pytest.fixture()
def client():
    app.config["TESTING"] = True
    requests_db.clear()
    with app.test_client() as client:
        yield client
    requests_db.clear()


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json["status"] == "healthy"


def test_home(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json["application"] == "LabCloud"


def test_get_all_requests(client):
    response = client.get("/api/requests")
    assert response.status_code == 200
    assert response.json == []


def test_create_request(client):
    response = client.post("/api/requests", json={
        "title": "Компьютерді тексеру",
        "category": "computer",
        "priority": "medium",
        "description": "Жұмысын тексеру"
    })
    assert response.status_code == 201
    assert response.json["id"] == 1


def test_invalid_category(client):
    response = client.post("/api/requests", json={
        "title": "Тест",
        "category": "unknown",
        "priority": "high"
    })
    assert response.status_code == 400


def test_invalid_priority(client):
    response = client.post("/api/requests", json={
        "title": "Тест",
        "category": "network",
        "priority": "urgent"
    })
    assert response.status_code == 400


def test_empty_title(client):
    response = client.post("/api/requests", json={
        "title": "   ",
        "category": "network",
        "priority": "low"
    })
    assert response.status_code == 400


def test_invalid_json(client):
    response = client.post(
        "/api/requests",
        data="{bad json",
        content_type="application/json"
    )
    assert response.status_code == 400


def test_title_wrong_type(client):
    response = client.post("/api/requests", json={
        "title": 123,
        "category": "computer",
        "priority": "low"
    })
    assert response.status_code == 400


def test_description_wrong_type(client):
    response = client.post("/api/requests", json={
        "title": "Тест",
        "category": "computer",
        "priority": "low",
        "description": 123
    })
    assert response.status_code == 400


def test_title_too_long(client):
    response = client.post("/api/requests", json={
        "title": "A" * 121,
        "category": "computer",
        "priority": "low"
    })
    assert response.status_code == 400


def test_missing_title(client):
    response = client.post("/api/requests", json={
        "category": "network",
        "priority": "high"
    })
    assert response.status_code == 400


def test_read_created_request(client):
    created = client.post("/api/requests", json={
        "title": "Желіні тексеру",
        "category": "network",
        "priority": "high"
    })
    request_id = created.json["id"]
    response = client.get(f"/api/requests/{request_id}")
    assert response.status_code == 200
    assert response.json["title"] == "Желіні тексеру"


def test_missing_request(client):
    response = client.get("/api/requests/999")
    assert response.status_code == 404
