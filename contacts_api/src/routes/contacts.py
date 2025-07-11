from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from src.schemas.contacts import *
from src.database.db import get_db
from src.repository import contacts as repo
from src.database.models import User
from src.services.auth import auth_service
from fastapi_limiter.depends import RateLimiter

router = APIRouter(prefix="/contacts", tags=["contacts"])


# Route: POST /contacts/
# Purpose: Create a new contact for the authenticated user
# Method: POST
# Accepts: ContactCreate
# Returns: ContactResponse
@router.post(
    "/",
    response_model=ContactResponse,
    dependencies=[Depends(RateLimiter(times=2, seconds=300))],
)
def create(
    contact: ContactCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    return repo.create_contact(db, contact, current_user)


# Route: GET /contacts/
# Purpose: Retrieve all contacts of the authenticated user
# Method: GET
# Returns: List of ContactResponse
@router.get("/", response_model=List[ContactResponse])
def read_all(
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    return repo.get_contacts(db, current_user)


# Route: GET /contacts/{contact_id}
# Purpose: Retrieve a single contact by ID
# Method: GET
# Accepts: contact_id (int)
# Returns: ContactResponse
# Status Codes:
#   404 – contact not found
@router.get("/{contact_id}", response_model=ContactResponse)
def read_one(
    contact_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    contact = repo.get_contact_by_id(db, contact_id, current_user)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact


# Route: PUT /contacts/{contact_id}
# Purpose: Update a contact by ID
# Method: PUT
# Accepts: contact_id (int), ContactUpdate
# Returns: ContactResponse
# Status Codes:
#   404 – contact not found
@router.put("/{contact_id}", response_model=ContactResponse)
def update(
    contact_id: int,
    contact: ContactUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    updated_contact = repo.update_contact(db, contact_id, contact, current_user)
    if not updated_contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return updated_contact


# Route: DELETE /contacts/{contact_id}
# Purpose: Delete a contact by ID
# Method: DELETE
# Accepts: contact_id (int)
# Returns: Deleted ContactResponse
# Status Codes:
#   404 – contact not found
@router.delete("/{contact_id}", response_model=ContactResponse)
def delete(
    contact_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    deleted_contact = repo.delete_contact(db, contact_id, current_user)
    if not deleted_contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    return deleted_contact


# Route: GET /contacts/search/{query}
# Purpose: Search contacts by name or email
# Method: GET
# Accepts: query (str)
# Returns: List of ContactResponse
@router.get("/search/{query}", response_model=List[ContactResponse])
def search(
    query: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    return repo.search_contacts(query, db, current_user)


# Route: GET /contacts/birthdays/upcoming
# Purpose: Get contacts with birthdays in the upcoming 7 days
# Method: GET
# Returns: List of ContactResponse
@router.get("/birthdays/upcoming", response_model=List[ContactResponse])
def birthdays(
    db: Session = Depends(get_db),
    current_user: User = Depends(auth_service.get_current_user),
):
    return repo.upcoming_birthdays(db, current_user)
