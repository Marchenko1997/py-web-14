"""
Security dependencies using FastAPI's built-in classes
"""

from fastapi.security import OAuth2PasswordBearer, HTTPBearer

API_PREFIX = "/api"

# OAuth2 password flow for token-based login
oauth2_scheme = OAuth2PasswordBearer(tokenUrl=f"{API_PREFIX}/auth/login")

# HTTP Bearer scheme (Authorization: Bearer <token>)
http_bearer = HTTPBearer()
