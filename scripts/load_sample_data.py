"""샘플 포지션 데이터 로딩 스크립트"""

from __future__ import annotations

import asyncio
import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
logger = logging.getLogger(__name__)


async def main() -> None:
    from hdesk.data.database import get_db_session
    from hdesk.data.repositories.position_repo import PositionRepository
    from hdesk.data.seeds.sample_positions import get_sample_positions

    async with get_db_session() as session:
        repo = PositionRepository(session)
        existing = await repo.get_all_active()

        if existing:
            logger.warning("이미 %d개 포지션 존재 - 스킵", len(existing))
            return

        positions = get_sample_positions()
        for pos in positions:
            created = await repo.create(pos)
            logger.info(
                "포지션 생성: ID=%d, %s %s K=%.1f Q=%d",
                created.id,
                created.underlying,
                created.option_type or "FUTURE",
                created.strike or 0,
                created.quantity,
            )

    logger.info("샘플 데이터 로딩 완료: %d개 포지션", len(positions))


if __name__ == "__main__":
    asyncio.run(main())
