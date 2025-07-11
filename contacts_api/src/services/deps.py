"""
Dependency provider for Redis client
"""

from fastapi import Request


async def get_redis(request: Request):
    """
    Return Redis client from app state
    """
    return request.app.state.redis
