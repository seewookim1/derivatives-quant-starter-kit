"""리스크 결과 레포지토리"""

from __future__ import annotations

from datetime import date
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from hdesk.data.models.risk_snapshot import VaRResult


class RiskRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save_var_result(self, result: VaRResult) -> VaRResult:
        self._session.add(result)
        await self._session.flush()
        return result

    async def get_latest_var(
        self, method: str = "historical", confidence: float = 0.99
    ) -> Optional[VaRResult]:
        result = await self._session.execute(
            select(VaRResult)
            .where(VaRResult.method == method, VaRResult.confidence == confidence)
            .order_by(VaRResult.calc_date.desc())
            .limit(1)
        )
        return result.scalar_one_or_none()

    async def get_var_history(
        self, method: str = "historical", days: int = 30
    ) -> list[VaRResult]:
        result = await self._session.execute(
            select(VaRResult)
            .where(VaRResult.method == method)
            .order_by(VaRResult.calc_date.desc())
            .limit(days)
        )
        return list(result.scalars().all())
