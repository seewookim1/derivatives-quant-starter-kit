"""FastAPI 애플리케이션 진입점"""

from __future__ import annotations

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

import redis.asyncio as aioredis
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from hdesk.api.routers import greeks, health, market_data, positions, risk
from hdesk.api.websocket.manager import ConnectionManager
from hdesk.data.database import engine, init_db
from hdesk.utils.config import get_settings
from hdesk.utils.logging import setup_logging

logger = logging.getLogger(__name__)
settings = get_settings()

# 글로벌 WebSocket 연결 매니저
ws_manager = ConnectionManager()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """앱 시작/종료 이벤트."""
    setup_logging(settings.log_level, settings.log_format)
    logger.info("HDesk API 시작 중...")

    # DB 테이블 생성 (SQLAlchemy 관리 테이블만)
    await init_db()

    # Redis 연결
    redis_client = aioredis.from_url(settings.redis_url, decode_responses=True)
    app.state.redis = redis_client
    app.state.ws_manager = ws_manager

    # Redis → WebSocket 브리지 시작
    await ws_manager.start_redis_listener(redis_client)
    logger.info("HDesk API 준비 완료")

    yield

    logger.info("HDesk API 종료 중...")
    await ws_manager.stop()
    await redis_client.aclose()
    await engine.dispose()


app = FastAPI(
    title="HDesk API",
    description="Derivatives Hedge Desk Risk Management API",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(health.router)
app.include_router(positions.router, prefix="/api/v1")
app.include_router(greeks.router, prefix="/api/v1")
app.include_router(risk.router, prefix="/api/v1")
app.include_router(market_data.router, prefix="/api/v1")


def run() -> None:
    import uvicorn

    uvicorn.run(
        "hdesk.api.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.api_debug,
    )
