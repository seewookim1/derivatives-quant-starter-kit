"""FastAPI 의존성 주입"""

from __future__ import annotations

from typing import AsyncGenerator

import redis.asyncio as aioredis
from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from hdesk.data.database import AsyncSessionLocal


async def get_db(request: Request) -> AsyncGenerator[AsyncSession, None]:
    """DB 세션 의존성."""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def get_redis(request: Request) -> aioredis.Redis:
    """Redis 클라이언트 의존성."""
    return request.app.state.redis
