import json
import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from src.database.models import User
from src.services.auth import auth_service
from src.main import app


@pytest.fixture()
def token(client, user, session):
    # Мокаем функцию отправки email
    with patch("src.routes.auth.send_verification_email", new_callable=AsyncMock):
        client.post("/api/auth/signup", json=user)

    current_user: User = (
        session.query(User).filter(User.email == user.get("email")).first()
    )
    current_user.confirmed = True
    session.commit()

    response = client.post(
        "/api/auth/login",
        data={"username": user.get("email"), "password": user.get("password")},
    )
    return response.json()["access_token"]


@pytest.fixture()
def contact_data():
    return {
        "first_name": "John",
        "last_name": "Doe",
        "email": "john.doe@example.com",
        "phone": "1234567890",
        "birthday": "1990-01-01",
    }


def test_create_contact(client, token, session, user, contact_data):
    current_user = session.query(User).filter(User.email == user["email"]).first()

    auth_service.r = AsyncMock()

   
    async def mock_get_current_user():
        return current_user

    app.dependency_overrides[auth_service.get_current_user] = mock_get_current_user

    response = client.post(
        "/api/contacts/",
        json=contact_data,
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 201, response.text
    data = response.json()
    assert data["email"] == contact_data["email"]


def test_read_all_contacts(client, token, session, user):
    current_user = session.query(User).filter(User.email == user["email"]).first()

 
    async def mock_get_current_user():
        return current_user

    app.dependency_overrides[auth_service.get_current_user] = mock_get_current_user

    response = client.get(
        "/api/contacts/",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

   
    app.dependency_overrides = {}


def test_read_one_contact(client, token, user, contact_data):
   
    mock_redis = AsyncMock()
    mock_redis.get.return_value = None
    mock_redis.set.return_value = None
    auth_service.r = mock_redis

   
    from src.database.db import get_db
    from src.database.models import User

    db = next(get_db())
    current_user = db.query(User).filter(User.email == user["email"]).first()

   
    async def mock_get_current_user():
        return current_user

    app.dependency_overrides[auth_service.get_current_user] = mock_get_current_user

   
    create_response = client.post(
        "/api/contacts/",
        json=contact_data,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert create_response.status_code == 201
    created_contact = create_response.json()


    response = client.get(
        f"/api/contacts/{created_contact['id']}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json()["id"] == created_contact["id"]


    app.dependency_overrides = {}


def test_read_one_contact_not_found(client, token):
    user_data = {
        "id": 1,
        "email": "deadpool@example.com",
        "confirmed": True,
        "password": "hashed_password",  
    }

    mock_redis = AsyncMock()
    mock_redis.get.return_value = json.dumps(user_data)
    mock_redis.set.return_value = None
    auth_service.r = mock_redis

    async def mock_get_current_user():
        return User(**user_data)

    app.dependency_overrides[auth_service.get_current_user] = mock_get_current_user

    response = client.get(
        "/api/contacts/9999",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Contact not found"


def test_update_contact(client, token):
    with patch.object(auth_service, "r") as r_mock:
        r_mock.get.return_value = None
        r_mock.set.return_value = None

     
        contact_data = {
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "phone": "+1234567890",
            "birthday": "1990-01-01",
        }

        create_response = client.post(
            "/api/contacts/",
            json=contact_data,
            headers={"Authorization": f"Bearer {token}"},
        )
        assert create_response.status_code == 201
        created_id = create_response.json()["id"]

       
        updated = {
            "first_name": "Updated",
            "last_name": "Name",
            "email": "updated@example.com",
            "phone": "+1234567890",
            "birthday": "1991-01-01",
        }

        response = client.put(
            f"/api/contacts/{created_id}",
            json=updated,
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["first_name"] == "Updated"
        assert data["email"] == "updated@example.com"


def test_update_contact_not_found(client, token):
    with patch.object(auth_service, "r") as r_mock:
        r_mock.get.return_value = None
        r_mock.set.return_value = None

        update_data = {
            "first_name": "Test",
            "last_name": "NotFound",
            "email": "notfound@example.com",
            "phone": "+1234567890",
            "birthday": "1990-01-01",
        }

        response = client.put(
            "/api/contacts/9999",
            json=update_data,
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 404
        assert response.json()["detail"] == "Contact not found"


def test_delete_contact(client, token):
    with patch.object(auth_service, "r") as r_mock:
        r_mock.get.return_value = None
        r_mock.set.return_value = None

      
        contact_data = {
            "first_name": "ToDelete",
            "last_name": "User",
            "email": "delete@example.com",
            "phone": "+1111111111",
            "birthday": "1992-02-02",
        }

        create_response = client.post(
            "/api/contacts/",
            json=contact_data,
            headers={"Authorization": f"Bearer {token}"},
        )
        assert create_response.status_code == 201
        contact_id = create_response.json()["id"]

       
        delete_response = client.delete(
            f"/api/contacts/{contact_id}", headers={"Authorization": f"Bearer {token}"}
        )

        assert delete_response.status_code == 200
        assert delete_response.json()["id"] == contact_id


def test_delete_contact_not_found(client, token):
    with patch.object(auth_service, "r") as r_mock:
        r_mock.get.return_value = None

        response = client.delete(
            "/api/contacts/9999", headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 404
        assert response.json()["detail"] == "Contact not found"


def test_search_contacts(client, token):
    with patch.object(auth_service, "r") as r_mock:
        r_mock.get.return_value = None

        response = client.get(
            "/api/contacts/search/john", headers={"Authorization": f"Bearer {token}"}
        )
        assert response.status_code == 200
        assert isinstance(response.json(), list)


def test_upcoming_birthdays(client, token):
    with patch.object(auth_service, "r") as r_mock:
        r_mock.get.return_value = None

        response = client.get(
            "/api/contacts/birthdays/upcoming",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert response.status_code == 200
        assert isinstance(response.json(), list)
