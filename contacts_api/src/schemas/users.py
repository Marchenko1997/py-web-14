from pydantic import BaseModel, Field, EmailStr
from datetime import datetime

# Schema for user registration/login
class UserModel(BaseModel):
    email: str
    password: str = Field(min_length=6, max_length=20)

# Schema for returning basic user information
class UserResponse(BaseModel):
    id: int
    email: str
    created_at: datetime  # Account creation timestamp

    class Config:
        orm_mode = True  # Enables compatibility with ORM models

# Schema for returning access and refresh tokens
class TokenModel(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"  # Type of token (default: bearer)

# Schema for initiating password reset request
class RequestResetModel(BaseModel):
    email: EmailStr

# Schema for resetting the password using a token
class ResetPasswordModel(BaseModel):
    email: EmailStr
    token: str  # Token received by email
    new_password: str  # New password to set
