from sqlalchemy.orm import Session
from src.database.models import User
from src.schemas.users import UserModel
from sqlalchemy import update


async def get_user_by_email(email: str, db: Session):
    """
    Retrieve a user by email address.

    Args:
        email (str): Email address of the user.
        db (Session): SQLAlchemy database session.

    Returns:
        User | None: User object if found, otherwise None.
    """
    return db.query(User).filter(User.email == email).first()


async def create_user(body: UserModel, db: Session):
    """
    Create a new user in the database.

    Args:
        body (UserModel): User input model with email and password.
        db (Session): SQLAlchemy database session.

    Returns:
        User: Newly created user object.
    """
    user = User(email=body.email, password=body.password)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


async def update_token(user: User, token: str | None, db: Session):
    """
    Update the refresh token for a user.

    Args:
        user (User): User whose token is being updated.
        token (str | None): New refresh token or None.
        db (Session): SQLAlchemy database session.
    """
    user.refresh_token = token
    db.commit()


async def confirm_email(email: str, db: Session):
    """
    Mark a user's email as confirmed.

    Args:
        email (str): Email address to confirm.
        db (Session): SQLAlchemy database session.

    Returns:
        User | None: Updated user object if found, otherwise None.
    """
    user = await get_user_by_email(email, db)
    if user:
        user.confirmed = True
        db.commit()
        db.refresh(user)
        return user


async def update_avatar(user: User, url: str, db: Session) -> User:
    """
    Update the avatar URL for a user.

    Args:
        user (User): The user whose avatar is being updated.
        url (str): New avatar URL.
        db (Session): SQLAlchemy database session.

    Returns:
        User: Updated user object.
    """
    user.avatar = url
    db.commit()
    db.refresh(user)
    return user


async def update_password(email: str, hashed_password: str, db: Session):
    """
    Update the password for a user by email.

    Args:
        email (str): Email address of the user.
        hashed_password (str): New hashed password.
        db (Session): SQLAlchemy database session.
    """
    user = await get_user_by_email(email, db)
    if user:
        user.password = hashed_password
        db.commit()
        db.refresh(user)
