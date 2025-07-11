from pydantic import BaseModel, EmailStr, Field
from datetime import date
from typing import Optional

# Base schema for contact data (used in create and update)
class ContactBase(BaseModel):
    first_name: str = Field(max_length=50)
    last_name: str = Field(max_length=50)
    email: EmailStr
    phone: str = Field(max_length=20)
    birthday: date
    additional_info: Optional[str] = None

# Schema for creating a new contact (inherits all fields from ContactBase)
class ContactCreate(ContactBase):
    pass
# Schema for updating an existing contact (same fields as creation)
class ContactUpdate(ContactBase):
    pass
# Schema for returning contact information from API
class ContactResponse(ContactBase):
    id: int

    class Config:
        orm_mode = True  # Enables compatibility with ORM models
