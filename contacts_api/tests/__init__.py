# tests/__init__.py

import os

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
