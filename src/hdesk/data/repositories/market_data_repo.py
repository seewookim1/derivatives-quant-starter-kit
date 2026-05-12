"""시장 데이터 레포지토리"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional

import pandas as pd
from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from hdesk.data.models.market_data import GreeksSnapshot, MarketData


class MarketDataRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def get_latest_price(self, symbol: str) -> Optional[float]:
        result = await self._session.execute(
            select(MarketData.price)
            .where(MarketData.symbol == symbol)
            .order_by(MarketData.timestamp.desc())
            .limit(1)
        )
        row = result.scalar_one_or_none()
        return row

    async def get_price_history(
        self, symbol: str, days: int = 252
    ) -> pd.DataFrame:
        """TimescaleDB time_bucket으로 일별 종가 조회."""
        since = datetime.utcnow() - timedelta(days=days)
        result = await self._session.execute(
            text("""
                SELECT
                    time_bucket('1 day', timestamp) AS bucket,
                    last(price, timestamp) AS close
                FROM market_data
                WHERE symbol = :symbol AND timestamp >= :since
                GROUP BY bucket
                ORDER BY bucket
            """),
            {"symbol": symbol, "since": since},
        )
        rows = result.fetchall()
        if not rows:
            return pd.DataFrame(columns=["date", "close"])
        return pd.DataFrame(rows, columns=["date", "close"])

    async def insert_tick(self, tick: MarketData) -> None:
        self._session.add(tick)
        await self._session.flush()

    async def insert_greeks_snapshot(self, snapshot: GreeksSnapshot) -> None:
        self._session.add(snapshot)
        await self._session.flush()

    async def get_greeks_history(
        self, position_id: int, hours: int = 8
    ) -> list[GreeksSnapshot]:
        since = datetime.utcnow() - timedelta(hours=hours)
        result = await self._session.execute(
            select(GreeksSnapshot)
            .where(
                GreeksSnapshot.position_id == position_id,
                GreeksSnapshot.timestamp >= since,
            )
            .order_by(GreeksSnapshot.timestamp)
        )
        return list(result.scalars().all())
