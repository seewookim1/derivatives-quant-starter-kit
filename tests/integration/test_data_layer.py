"""데이터 레이어 통합 테스트

실행 전 필요: Docker TimescaleDB
"""

from __future__ import annotations

import pytest


@pytest.mark.asyncio
@pytest.mark.skipif(
    True,  # DB 연결 필요 시 False로 변경
    reason="TimescaleDB 연결 필요",
)
async def test_position_crud():
    """포지션 CRUD 통합 테스트."""
    from datetime import date

    from hdesk.data.database import get_db_session
    from hdesk.data.models.position import Position
    from hdesk.data.repositories.position_repo import PositionRepository

    async with get_db_session() as session:
        repo = PositionRepository(session)

        position = Position(
            underlying="KOSPI200",
            instrument_type="OPTION",
            option_type="C",
            strike=350.0,
            expiry=date(2025, 6, 12),
            quantity=10,
            multiplier=250_000,
            avg_price=5.50,
        )
        created = await repo.create(position)
        assert created.id is not None

        fetched = await repo.get_by_id(created.id)
        assert fetched is not None
        assert fetched.underlying == "KOSPI200"

        await repo.deactivate(created.id)
        fetched_again = await repo.get_by_id(created.id)
        assert fetched_again is not None
        assert fetched_again.is_active is False
