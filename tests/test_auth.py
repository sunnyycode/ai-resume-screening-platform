import pytest
from backend import create_app
from backend.database import db
from config import TestConfig

@pytest.fixture
def client():
    app = create_app(TestConfig)
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.session.remove()
            db.drop_all()

def test_user_registration_success(client):
    response = client.post(
        "/api/auth/register",
        json={
            "name": "Jane Doe",
            "email": "jane.doe@example.com",
            "password": "securePassword123"
        }
    )
    assert response.status_code == 201
    data = response.get_json()
    assert data["success"] is True
    assert "token" in data
    assert data["user"]["email"] == "jane.doe@example.com"

def test_user_registration_duplicate_email(client):
    payload = {
        "name": "Jane Doe",
        "email": "jane.doe@example.com",
        "password": "securePassword123"
    }
    client.post("/api/auth/register", json=payload)
    response = client.post("/api/auth/register", json=payload)
    assert response.status_code == 400
    data = response.get_json()
    assert data["success"] is False
    assert "already exists" in data["error"]

def test_user_registration_invalid_email(client):
    response = client.post(
        "/api/auth/register",
        json={
            "name": "Jane",
            "email": "not-an-email",
            "password": "securePassword123"
        }
    )
    assert response.status_code == 400
    assert response.get_json()["success"] is False

def test_user_registration_weak_password(client):
    response = client.post(
        "/api/auth/register",
        json={
            "name": "Jane",
            "email": "jane@example.com",
            "password": "123"
        }
    )
    assert response.status_code == 400
    assert "at least 6 characters" in response.get_json()["error"]

def test_user_login_success(client):
    client.post(
        "/api/auth/register",
        json={
            "name": "Jane",
            "email": "jane@example.com",
            "password": "password123"
        }
    )
    response = client.post(
        "/api/auth/login",
        json={
            "email": "jane@example.com",
            "password": "password123"
        }
    )
    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert "token" in data

def test_user_login_invalid_password(client):
    client.post(
        "/api/auth/register",
        json={
            "name": "Jane",
            "email": "jane@example.com",
            "password": "password123"
        }
    )
    response = client.post(
        "/api/auth/login",
        json={
            "email": "jane@example.com",
            "password": "wrongpassword"
        }
    )
    assert response.status_code == 401
    assert response.get_json()["success"] is False

def test_protected_route_without_token(client):
    response = client.get("/api/auth/me")
    assert response.status_code == 401
