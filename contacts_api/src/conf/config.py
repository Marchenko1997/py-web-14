"""
config.py — configuration settings for the Contacts API application.

This module:
- Loads environment variables from a .env file
- Provides settings for the database, JWT, email, Cloudinary, and Redis
"""

from pydantic_settings import BaseSettings
from pydantic import EmailStr


class Settings(BaseSettings):
    """
    Configuration class that loads environment variables using Pydantic.

    Attributes:
        database_url (str): PostgreSQL database connection URL
        secret_key (str): Secret key for JWT token generation
        algorithm (str): JWT signing algorithm (default: HS256)
        mail_username (EmailStr): Email username for SMTP
        mail_password (str): Password for SMTP
        mail_from (EmailStr): Default sender email address
        mail_port (int): SMTP port
        mail_server (str): SMTP server address
        mail_from_name (str): Display name for sender
        email_secret_key (str): Secret key for email verification tokens
        base_url (str): Base URL of the frontend application
        cloudinary_name (str): Cloudinary account name
        cloudinary_api_key (str): Cloudinary API key
        cloudinary_api_secret (str): Cloudinary API secret
        redis_host (str): Redis server hostname (default: localhost)
        redis_port (int): Redis server port (default: 6379)
    """

    database_url: str
    secret_key: str
    algorithm: str = "HS256"

    mail_username: EmailStr
    mail_password: str
    mail_from: EmailStr
    mail_port: int
    mail_server: str
    mail_from_name: str
    email_secret_key: str
    base_url: str

    cloudinary_name: str
    cloudinary_api_key: str
    cloudinary_api_secret: str

    redis_host: str = "localhost"
    redis_port: int = 6379

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
