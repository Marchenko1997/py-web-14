from sqlalchemy.orm import Session
from src.database.models import Contact, User
from src.schemas.contacts import ContactCreate, ContactUpdate
from datetime import datetime, timedelta


def create_contact(db: Session, contact: ContactCreate, user: User):
    """
    Create a new contact for a specific user.

    Args:
        db (Session): SQLAlchemy database session.
        contact (ContactCreate): Pydantic model with contact data.
        user (User): The user who owns the contact.

    Returns:
        Contact: The newly created contact object.
    """
    new_contact = Contact(**contact.model_dump(), user_id=user.id)
    db.add(new_contact)
    db.commit()
    db.refresh(new_contact)
    return new_contact


def get_contacts(db: Session, user: User):
    """
    Retrieve all contacts belonging to a specific user.

    Args:
        db (Session): SQLAlchemy database session.
        user (User): The user whose contacts to retrieve.

    Returns:
        List[Contact]: List of contact objects.
    """
    return db.query(Contact).filter(Contact.user_id == user.id).all()


def get_contact_by_id(db: Session, contact_id: int, user: User):
    """
    Retrieve a single contact by its ID and user.

    Args:
        db (Session): SQLAlchemy database session.
        contact_id (int): ID of the contact to retrieve.
        user (User): The user who owns the contact.

    Returns:
        Contact | None: Contact object if found, otherwise None.
    """
    return (
        db.query(Contact)
        .filter(Contact.id == contact_id, Contact.user_id == user.id)
        .first()
    )


def update_contact(db: Session, contact_id: int, data: ContactUpdate, user: User):
    """
    Update an existing contact by ID for a specific user.

    Args:
        db (Session): SQLAlchemy database session.
        contact_id (int): ID of the contact to update.
        data (ContactUpdate): New contact data.
        user (User): The user who owns the contact.

    Returns:
        Contact | None: Updated contact object if found and updated, otherwise None.
    """
    contact = get_contact_by_id(db, contact_id, user)
    if contact:
        for key, value in data.model_dump().items():
            setattr(contact, key, value)
        db.commit()
        db.refresh(contact)
    return contact


def delete_contact(db: Session, contact_id: int, user: User):
    """
    Delete a contact by ID for a specific user.

    Args:
        db (Session): SQLAlchemy database session.
        contact_id (int): ID of the contact to delete.
        user (User): The user who owns the contact.

    Returns:
        Contact | None: Deleted contact object if found and removed, otherwise None.
    """
    contact = get_contact_by_id(db, contact_id, user)
    if contact:
        db.delete(contact)
        db.commit()
    return contact


def search_contacts(query: str, db: Session, user: User):
    """
    Search contacts by name or email for a specific user.

    Args:
        query (str): Search string for first name, last name, or email.
        db (Session): SQLAlchemy database session.
        user (User): The user whose contacts to search.

    Returns:
        List[Contact]: Matching contact objects.
    """
    return (
        db.query(Contact)
        .filter(Contact.user_id == user.id)
        .filter(
            (Contact.first_name.ilike(f"%{query}%"))
            | (Contact.last_name.ilike(f"%{query}%"))
            | (Contact.email.ilike(f"%{query}%"))
        )
        .all()
    )


def upcoming_birthdays(db: Session, user: User):
    """
    Get contacts with birthdays in the next 7 days.

    Args:
        db (Session): SQLAlchemy database session.
        user (User): The user whose contacts to check.

    Returns:
        List[Contact]: Contacts with birthdays within the next 7 days.
    """
    today = datetime.today().date()
    next_week = today + timedelta(days=7)
    return (
        db.query(Contact)
        .filter(Contact.user_id == user.id)
        .filter(Contact.birthday.between(today, next_week))
        .all()
    )
