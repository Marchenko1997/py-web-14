import pytest
from unittest.mock import AsyncMock
from src.routes import auth
from src.services import deps
from src.main import app


# Мокаем отправку email
@pytest.fixture(autouse=True)
def mock_email(monkeypatch):
    monkeypatch.setattr(auth, "send_verification_email", AsyncMock())


# Мокаем Redis
@pytest.fixture(scope="module", autouse=True)
def override_redis_dependency():
    app.dependency_overrides[deps.get_redis] = AsyncMock(return_value=None)


def test_signup_user(client, user):
    response = client.post("/api/auth/signup", json=user)
    assert response.status_code == 201
    assert response.json()["email"] == user["email"]
    assert "id" in response.json()


def test_signup_duplicate_user(client, user):
    # Создаем пользователя вручную
    client.post("/api/auth/signup", json=user)

    # Пытаемся создать его снова
    response = client.post("/api/auth/signup", json=user)
    assert response.status_code == 409
    assert response.json()["detail"] == "Account already exists"


def test_login_user(client, user):
    # Убедимся, что пользователь зарегистрирован
    client.post("/api/auth/signup", json=user)

    response = client.post(
        "/api/auth/login",
        data={"username": user["email"], "password": user["password"]},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_user_invalid_password(client, user):
    # Убедимся, что пользователь зарегистрирован
    client.post("/api/auth/signup", json=user)

    response = client.post(
        "/api/auth/login",
        data={"username": user["email"], "password": "wrongpassword"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid password"


def test_login_user_not_found(client):
    response = client.post(
        "/api/auth/login",
        data={"username": "nonexistent@example.com", "password": "123456789"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email"
