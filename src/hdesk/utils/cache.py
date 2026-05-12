"""Redis 캐시 헬퍼"""

from __future__ import annotations

import json
import logging
from typing import Any

logger = logging.getLogger(__name__)


class RedisCache:
    """Greeks/VolSurface Redis 캐시."""

    GREEKS_KEY = "greeks:{position_id}"
    VOL_SURFACE_KEY = "vol_surface:{underlying}"
    PORTFOLIO_GREEKS_KEY = "portfolio:greeks"

    def __init__(self, redis_client: Any) -> None:
        self._redis = redis_client

    async def set_greeks(self, position_id: int, data: dict, ttl: int = 60) -> None:
        key = self.GREEKS_KEY.format(position_id=position_id)
        await self._redis.setex(key, ttl, json.dumps(data))

    async def get_greeks(self, position_id: int) -> dict | None:
        key = self.GREEKS_KEY.format(position_id=position_id)
        raw = await self._redis.get(key)
        return json.loads(raw) if raw else None

    async def set_vol_surface(self, underlying: str, data: dict, ttl: int = 300) -> None:
        key = self.VOL_SURFACE_KEY.format(underlying=underlying)
        await self._redis.setex(key, ttl, json.dumps(data))

    async def get_vol_surface(self, underlying: str) -> dict | None:
        key = self.VOL_SURFACE_KEY.format(underlying=underlying)
        raw = await self._redis.get(key)
        return json.loads(raw) if raw else None

    async def set_portfolio_greeks(self, data: dict, ttl: int = 30) -> None:
        await self._redis.setex(self.PORTFOLIO_GREEKS_KEY, ttl, json.dumps(data))

    async def get_portfolio_greeks(self) -> dict | None:
        raw = await self._redis.get(self.PORTFOLIO_GREEKS_KEY)
        return json.loads(raw) if raw else None

    async def publish(self, channel: str, message: dict) -> None:
        await self._redis.publish(channel, json.dumps(message))
