import json
from unittest.mock import MagicMock

import pytest
from jose import jwt

from src.database.models import User

SECRET_KEY = "testsecret"
ALGORITHM = "HS256"


def test_signup_user(client, user, monkeypatch):
    monkeypatch.setattr("src.routes.auth.send_verification_email", MagicMock())
    response = client.post("/api/auth/signup", json=user)
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == user["email"]
    assert "id" in data


def test_signup_duplicate_user(client, user):
    response = client.post("/api/auth/signup", json=user)
    assert response.status_code == 409
    assert response.json()["detail"] == "Account already exists"


def test_login_unconfirmed_user(client, user):
    response = client.post(
        "/api/auth/login",
        data={"username": user["email"], "password": user["password"]},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Email not verified"


def test_login_confirmed_user(client, session, user):
    current_user: User = session.query(User).filter(User.email == user["email"]).first()
    current_user.confirmed = True
    session.commit()

    response = client.post(
        "/api/auth/login",
        data={"username": user["email"], "password": user["password"]},
    )
    assert response.status_code == 200
    tokens = response.json()
    assert "access_token" in tokens
    assert "refresh_token" in tokens
    assert tokens["token_type"] == "bearer"


def test_login_wrong_password(client, user):
    response = client.post(
        "/api/auth/login", data={"username": user["email"], "password": "wrongpassword"}
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"


def test_login_wrong_email(client, user):
    response = client.post(
        "/api/auth/login",
        data={"username": "wrong@email.com", "password": user["password"]},
    )
    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid credentials"


def test_refresh_token(client, session, user):
    current_user: User = session.query(User).filter(User.email == user["email"]).first()
    current_user.confirmed = True
    session.commit()

    login_response = client.post(
        "/api/auth/login",
        data={"username": user["email"], "password": user["password"]},
    )
    refresh_token = login_response.json()["refresh_token"]

    response = client.get(
        "/api/auth/refresh_token", headers={"Authorization": f"Bearer {refresh_token}"}
    )

    assert response.status_code == 200
    tokens = response.json()
    assert "access_token" in tokens
    assert "refresh_token" in tokens


def test_logout(client, session, user):
    current_user: User = session.query(User).filter(User.email == user["email"]).first()
    current_user.confirmed = True
    session.commit()

    login_response = client.post(
        "/api/auth/login",
        data={"username": user["email"], "password": user["password"]},
    )
    access_token = login_response.json()["access_token"]

    response = client.post(
        "/api/auth/logout", headers={"Authorization": f"Bearer {access_token}"}
    )

    assert response.status_code == 204


def test_confirm_email(client, session, user):
    current_user: User = session.query(User).filter(User.email == user["email"]).first()
    token = jwt.encode({"sub": current_user.email}, SECRET_KEY, algorithm=ALGORITHM)

    response = client.get(f"/api/auth/confirm_email/{token}")
    assert response.status_code == 200
    assert response.json()["message"] in [
        "Email already confirmed",
        "Email confirmed successfully",
    ]


def test_request_reset_password(client, user, monkeypatch):
    monkeypatch.setattr("src.routes.auth.send_reset_email", MagicMock())
    response = client.post(
        "/api/auth/request-reset-password", json={"email": user["email"]}
    )
    assert response.status_code == 200
    assert response.json()["message"] == "Ссылка для сброса пароля отправлена на email"


def test_reset_password(client, user):
    token = "test-reset-token"
    client.app.state.redis.set(f"reset:{user['email']}", token)

    response = client.post(
        "/api/auth/reset-password",
        json={"email": user["email"], "token": token, "new_password": "newpassword123"},
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Пароль успешно обновлён"
