"""FastAPI 포지션 엔드포인트 통합 테스트

실행 전 필요: Docker TimescaleDB + Redis
pytest tests/integration/ --run-integration
"""

from __future__ import annotations

import pytest
import pytest_asyncio
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check():
    """헬스체크 엔드포인트."""
    from hdesk.api.main import app

    async with AsyncClient(app=app, base_url="http://test") as client:
        resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


@pytest.mark.asyncio
@pytest.mark.skipif(
    True,  # DB 연결 필요 시 False로 변경
    reason="TimescaleDB 연결 필요",
)
async def test_create_and_list_position():
    """포지션 생성 및 조회 통합 테스트."""
    from hdesk.api.main import app

    async with AsyncClient(app=app, base_url="http://test") as client:
        # 포지션 생성
        payload = {
            "underlying": "KOSPI200",
            "instrument_type": "OPTION",
            "option_type": "C",
            "strike": 350.0,
            "expiry": "2025-06-12",
            "quantity": 10,
            "multiplier": 250000,
            "avg_price": 5.50,
        }
        create_resp = await client.post("/api/v1/positions", json=payload)
        assert create_resp.status_code == 201

        position_id = create_resp.json()["id"]

        # 포지션 조회
        get_resp = await client.get(f"/api/v1/positions/{position_id}")
        assert get_resp.status_code == 200
        assert get_resp.json()["underlying"] == "KOSPI200"
