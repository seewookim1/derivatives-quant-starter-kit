"""WebSocket 연결 풀 관리 + Redis Pub/Sub 브리지"""

from __future__ import annotations

import asyncio
import json
import logging
from typing import Any

import redis.asyncio as aioredis
from fastapi import WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)

GREEKS_CHANNEL = "greeks:updates"
PNL_CHANNEL = "risk:portfolio"


class ConnectionManager:
    """WebSocket 연결 풀과 Redis Pub/Sub를 연결하는 브리지."""

    def __init__(self) -> None:
        self._greeks_connections: list[WebSocket] = []
        self._pnl_connections: list[WebSocket] = []
        self._listener_task: asyncio.Task | None = None
        self._running = False

    async def connect_greeks(self, ws: WebSocket) -> None:
        await ws.accept()
        self._greeks_connections.append(ws)
        logger.debug("Greeks WS 연결: 총 %d", len(self._greeks_connections))

    async def connect_pnl(self, ws: WebSocket) -> None:
        await ws.accept()
        self._pnl_connections.append(ws)

    def disconnect_greeks(self, ws: WebSocket) -> None:
        if ws in self._greeks_connections:
            self._greeks_connections.remove(ws)

    def disconnect_pnl(self, ws: WebSocket) -> None:
        if ws in self._pnl_connections:
            self._pnl_connections.remove(ws)

    async def broadcast_greeks(self, data: dict) -> None:
        await self._broadcast(self._greeks_connections, data)

    async def broadcast_pnl(self, data: dict) -> None:
        await self._broadcast(self._pnl_connections, data)

    async def _broadcast(self, connections: list[WebSocket], data: dict) -> None:
        dead: list[WebSocket] = []
        for ws in connections:
            try:
                await ws.send_json(data)
            except (WebSocketDisconnect, Exception):
                dead.append(ws)
        for ws in dead:
            if ws in connections:
                connections.remove(ws)

    async def start_redis_listener(self, redis_client: aioredis.Redis) -> None:
        self._running = True
        self._listener_task = asyncio.create_task(
            self._redis_listener(redis_client)
        )

    async def _redis_listener(self, redis_client: aioredis.Redis) -> None:
        pubsub = redis_client.pubsub()
        await pubsub.subscribe(GREEKS_CHANNEL, PNL_CHANNEL)
        logger.info("Redis 채널 구독: %s, %s", GREEKS_CHANNEL, PNL_CHANNEL)

        try:
            async for message in pubsub.listen():
                if not self._running:
                    break
                if message["type"] != "message":
                    continue
                try:
                    data = json.loads(message["data"])
                    channel = message["channel"]
                    if channel == GREEKS_CHANNEL:
                        await self.broadcast_greeks(data)
                    elif channel == PNL_CHANNEL:
                        await self.broadcast_pnl(data)
                except (json.JSONDecodeError, Exception) as e:
                    logger.warning("메시지 처리 실패: %s", e)
        except asyncio.CancelledError:
            pass
        finally:
            await pubsub.unsubscribe()
            await pubsub.aclose()

    async def stop(self) -> None:
        self._running = False
        if self._listener_task and not self._listener_task.done():
            self._listener_task.cancel()
            try:
                await self._listener_task
            except asyncio.CancelledError:
                pass
