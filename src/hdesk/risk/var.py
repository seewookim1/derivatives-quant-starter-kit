"""VaR 계산 - Historical 및 Parametric(Delta-Gamma) 방법론"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import numpy as np
import pandas as pd

if TYPE_CHECKING:
    from hdesk.risk.greeks_agg import PortfolioGreeks


@dataclass
class VaRResult:
    var_amount: float     # 손실액 (VaR)
    cvar_amount: float    # Expected Shortfall (CVaR)
    confidence: float
    horizon_days: int
    method: str
    lookback_days: int = 0


def historical_var(
    returns: pd.Series,
    confidence: float = 0.99,
    horizon_days: int = 1,
    lookback_days: int = 252,
) -> VaRResult:
    """역사적 시뮬레이션 VaR.

    Args:
        returns: 일별 P&L 시계열 (가장 최근 데이터가 마지막)
        confidence: VaR 신뢰 수준 (0.99 = 99%)
        horizon_days: 보유 기간 (일)
        lookback_days: 히스토리 기간

    Returns:
        VaRResult
    """
    if len(returns) < 10:
        raise ValueError(f"데이터 부족: {len(returns)}개 (최소 10개 필요)")

    recent = returns.tail(lookback_days).dropna()
    # 보유 기간 스케일링 (sqrt-of-time 규칙)
    scaled = recent * np.sqrt(horizon_days)

    alpha = 1.0 - confidence
    var = float(-np.percentile(scaled, alpha * 100))
    cvar = float(-scaled[scaled <= -var].mean()) if (scaled <= -var).any() else var

    return VaRResult(
        var_amount=var,
        cvar_amount=cvar,
        confidence=confidence,
        horizon_days=horizon_days,
        method="historical",
        lookback_days=len(recent),
    )


def parametric_var(
    portfolio_greeks: "PortfolioGreeks",
    vol_of_underlying: float,
    underlying_price: float,
    confidence: float = 0.99,
    horizon_days: int = 1,
) -> VaRResult:
    """Delta-Gamma 근사 VaR.

    1일 P&L ≈ Delta * dS + 0.5 * Gamma * dS²

    Args:
        portfolio_greeks: 포트폴리오 집계 Greeks
        vol_of_underlying: 기초자산 변동성 (연율)
        underlying_price: 기초자산 현재가
        confidence: VaR 신뢰 수준
        horizon_days: 보유 기간

    Returns:
        VaRResult
    """
    from scipy.stats import norm

    # 일별 변동성으로 환산
    daily_vol = vol_of_underlying / np.sqrt(252)
    daily_sigma_S = underlying_price * daily_vol * np.sqrt(horizon_days)

    # 신뢰 수준에 대응하는 z-score
    z = norm.ppf(confidence)

    # Delta P&L (1차 근사)
    delta_pnl = portfolio_greeks.net_delta * daily_sigma_S * z

    # Gamma 조정 (2차 항): 0.5 * Gamma * (z * sigma_S)^2
    gamma_adj = 0.5 * portfolio_greeks.net_gamma * (daily_sigma_S * z) ** 2

    var = delta_pnl + gamma_adj
    # CVaR = VaR * phi(z) / (1 - confidence) (정규 분포 가정)
    cvar = float(norm.pdf(z) / (1 - confidence)) * var

    return VaRResult(
        var_amount=float(var),
        cvar_amount=float(cvar),
        confidence=confidence,
        horizon_days=horizon_days,
        method="parametric",
    )
