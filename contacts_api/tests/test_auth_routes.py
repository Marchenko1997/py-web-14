import pytest
from unittest.mock import AsyncMock
from src.routes import auth
from src.services import deps
from src.main import app
from urllib.parse import urlencode
from src.database.models import User


@pytest.fixture(autouse=True)
def mock_redis(monkeypatch):
    monkeypatch.setattr(deps, "get_redis", AsyncMock(return_value=AsyncMock()))


# Мокаем отправку email
@pytest.fixture(autouse=True)
def mock_email(monkeypatch):
    monkeypatch.setattr(auth, "send_verification_email", AsyncMock())



def test_signup_user(client, user):
    response = client.post("/api/auth/signup", json=user)
    assert response.status_code == 201
    assert response.json()["email"] == user["email"]
    assert "id" in response.json()


def test_signup_duplicate_user(client, user):
    client.post("/api/auth/signup", json=user)  
    response = client.post("/api/auth/signup", json=user)  
    assert response.status_code == 409
    assert response.json()["detail"] == "Account already exists"


def test_login_user(client, session, user):
    # Регистрируем пользователя
    client.post("/api/auth/signup", json=user)

  
    current_user: User = session.query(User).filter(User.email == user["email"]).first()
    current_user.confirmed = True
    session.commit()


    response = client.post(
        "/api/auth/login",
        data={"username": user["email"], "password": user["password"]},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )

    assert response.status_code == 200, response.text
    data = response.json()
    assert data["token_type"] == "bearer"
    assert "access_token" in data


def test_login_user_invalid_password(client, session, user):
    client.post("/api/auth/signup", json=user)

   
    current_user: User = session.query(User).filter(User.email == user["email"]).first()
    current_user.confirmed = True
    session.commit()

    response = client.post(
        "/api/auth/login",
        data={"username": user["email"], "password": "wrongpassword"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"


def test_login_user_not_found(client, user):
    response = client.post(
        "/api/auth/login",
        data={"username": "notfound@example.com", "password": user["password"]},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"
