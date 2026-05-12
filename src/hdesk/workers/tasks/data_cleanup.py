"""오래된 데이터 정리 태스크"""

from __future__ import annotations

import asyncio
import logging

logger = logging.getLogger(__name__)


def cleanup_old_data() -> None:
    """90일 초과 틱 데이터 삭제 (동기 래퍼).

    TimescaleDB의 보존 정책(add_retention_policy)이 설정되어 있으면
    이 태스크는 추가 안전장치로만 동작.
    """
    asyncio.run(_cleanup_async())


async def _cleanup_async() -> None:
    from sqlalchemy.ext.asyncio import create_async_engine
    from sqlalchemy import text

    from hdesk.utils.config import get_settings

    settings = get_settings()
    engine = create_async_engine(settings.database_url)

    async with engine.connect() as conn:
        result = await conn.execute(
            text("DELETE FROM market_data WHERE timestamp < NOW() - INTERVAL '90 days'")
        )
        await conn.commit()
        logger.info("틱 데이터 정리 완료: %d행 삭제", result.rowcount)

    await engine.dispose()
