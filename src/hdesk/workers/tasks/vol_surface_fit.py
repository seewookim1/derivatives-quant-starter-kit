"""변동성 서피스 재보정 태스크"""

from __future__ import annotations

import asyncio
import logging

logger = logging.getLogger(__name__)


def refresh_vol_surface() -> None:
    """변동성 서피스 재보정 및 Redis 캐시 갱신 (동기 래퍼)."""
    asyncio.run(_refresh_async())


async def _refresh_async() -> None:
    import redis.asyncio as aioredis

    from hdesk.pricing.vol_surface import VolSurface
    from hdesk.utils.cache import RedisCache
    from hdesk.utils.config import get_settings

    settings = get_settings()

    # 실제 구현: Bloomberg에서 IV 매트릭스 가져와 VolSurface 재보정
    # 여기서는 데모용 로직
    redis_client = aioredis.from_url(settings.redis_url, decode_responses=True)
    cache = RedisCache(redis_client)

    for underlying in ["KOSPI200", "005930 KS"]:
        try:
            surface = VolSurface.flat(0.20, underlying)
            await cache.set_vol_surface(underlying, surface.to_dict(), ttl=600)
            logger.debug("VolSurface 캐시 갱신: %s", underlying)
        except Exception as e:
            logger.warning("VolSurface 재보정 실패 (%s): %s", underlying, e)

    await redis_client.aclose()
