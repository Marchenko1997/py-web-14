import os
from unittest.mock import AsyncMock

os.environ["DATABASE_URL"] = "sqlite:///./test.db"
os.environ["SECRET_KEY"] = "test_secret"
os.environ["MAIL_USERNAME"] = "test@example.com"
os.environ["MAIL_PASSWORD"] = "testpassword"
os.environ["MAIL_FROM"] = "test@example.com"
os.environ["MAIL_PORT"] = "587"
os.environ["MAIL_SERVER"] = "smtp.example.com"
os.environ["MAIL_FROM_NAME"] = "Test Mailer"
os.environ["EMAIL_SECRET_KEY"] = "email_secret"
os.environ["BASE_URL"] = "http://localhost:8000"
os.environ["CLOUDINARY_NAME"] = "cloudinary_test"
os.environ["CLOUDINARY_API_KEY"] = "fake_key"
os.environ["CLOUDINARY_API_SECRET"] = "fake_secret"


import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.main import app
from src.database.models import Base
from src.database.db import get_db


SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def session():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="function")
def client(session):
    def override_get_db():
        try:
            yield session
        finally:
            session.close()

    app.dependency_overrides[get_db] = override_get_db

    app.state.redis = AsyncMock()

    return TestClient(app)


@pytest.fixture
def user():
    return {
        "username": "deadpool@example.com",
        "email": "deadpool@example.com",
        "password": "123456789",
    }
