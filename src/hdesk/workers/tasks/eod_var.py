"""EOD VaR 계산 태스크"""

from __future__ import annotations

import asyncio
import logging
from datetime import date

import pandas as pd

logger = logging.getLogger(__name__)


def run_eod_var() -> None:
    """EOD VaR 계산 및 저장 (동기 래퍼)."""
    asyncio.run(_run_eod_var_async())


async def _run_eod_var_async() -> None:
    from hdesk.data.database import get_db_session
    from hdesk.data.models.risk_snapshot import VaRResult as VaRResultModel
    from hdesk.data.repositories.market_data_repo import MarketDataRepository
    from hdesk.data.repositories.risk_repo import RiskRepository
    from hdesk.risk.var import historical_var
    from hdesk.utils.config import get_settings

    settings = get_settings()
    logger.info("EOD VaR 계산 시작")

    async with get_db_session() as session:
        md_repo = MarketDataRepository(session)
        risk_repo = RiskRepository(session)

        price_df = await md_repo.get_price_history(
            "KOSPI200", days=settings.default_var_lookback_days + 10
        )

        if len(price_df) < 30:
            logger.warning("VaR 계산 데이터 부족: %d건", len(price_df))
            return

        returns = price_df["close"].pct_change().dropna()

        for confidence in [0.95, 0.99]:
            result = historical_var(
                returns=pd.Series(returns.values),
                confidence=confidence,
                horizon_days=1,
                lookback_days=settings.default_var_lookback_days,
            )
            var_model = VaRResultModel(
                calc_date=date.today(),
                method="historical",
                confidence=confidence,
                horizon_days=1,
                var_amount=result.var_amount,
                cvar_amount=result.cvar_amount,
                lookback_days=result.lookback_days,
            )
            await risk_repo.save_var_result(var_model)
            logger.info(
                "VaR 저장 완료: confidence=%.2f, VaR=%.0f, CVaR=%.0f",
                confidence, result.var_amount, result.cvar_amount,
            )
