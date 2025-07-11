"""
main.py — the main entry point for the Contacts API FastAPI application.

This module:
- Initializes the FastAPI app
- Registers routes (contacts, auth, users)
- Configures CORS middleware
- Connects to Redis for rate limiting
"""

import redis.asyncio as redis
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_limiter import FastAPILimiter

from src.routes import contacts, auth, users
from src.conf.config import settings

app = FastAPI()

# Set allowed frontend origins
origins = ["http://localhost:3000"]

# Enable CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(contacts.router, prefix="/api")
app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")


@app.on_event("startup")
async def startup():
    """
    Initializes Redis on application startup.

    Redis is used for request rate limiting via FastAPILimiter.
    """
    redis_client = redis.Redis(
        host=settings.redis_host,
        port=settings.redis_port,
        db=0,
        encoding="utf-8",
        decode_responses=True,
    )
    await FastAPILimiter.init(redis_client)
    app.state.redis = redis_client


@app.get("/")
def root():
    """
    Root route for the API.

    Returns a confirmation that the Contacts API is running.
    """
    return {"message": "Contact API is running"}
