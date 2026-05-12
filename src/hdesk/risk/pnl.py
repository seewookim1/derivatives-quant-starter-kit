"""P&L 어트리뷰션 - Delta/Gamma/Vega/Theta 분해"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hdesk.risk.greeks_agg import PortfolioGreeks


@dataclass
class PnLAttribution:
    """P&L 어트리뷰션 결과."""

    total_pnl: float
    delta_pnl: float    # Delta * dS
    gamma_pnl: float    # 0.5 * Gamma * dS^2
    vega_pnl: float     # Vega * d_sigma (1% 단위)
    theta_pnl: float    # Theta * dt (1일)
    residual: float     # 설명 안 된 잔차

    def to_dict(self) -> dict:
        return {
            "total_pnl": self.total_pnl,
            "delta_pnl": self.delta_pnl,
            "gamma_pnl": self.gamma_pnl,
            "vega_pnl": self.vega_pnl,
            "theta_pnl": self.theta_pnl,
            "residual": self.residual,
        }


def compute_pnl_attribution(
    portfolio_greeks: "PortfolioGreeks",
    dS: float,          # 기초자산 가격 변화 (절대값)
    d_sigma: float,     # 변동성 변화 (% 단위, 예: +2.0 = +2%)
    dt_days: float = 1.0,
    actual_pnl: float | None = None,
) -> PnLAttribution:
    """포트폴리오 P&L 어트리뷰션.

    P&L ≈ Delta*dS + 0.5*Gamma*dS² + Vega*d_sigma + Theta*dt

    Args:
        portfolio_greeks: 포트폴리오 집계 Greeks
        dS: 기초자산 가격 변화 (절대값)
        d_sigma: 변동성 변화 (% 단위)
        dt_days: 경과 시간 (일)
        actual_pnl: 실제 P&L (잔차 계산용, None이면 잔차=0)

    Returns:
        PnLAttribution
    """
    delta_pnl = portfolio_greeks.net_delta * dS
    gamma_pnl = 0.5 * portfolio_greeks.net_gamma * dS ** 2
    vega_pnl = portfolio_greeks.net_vega * d_sigma  # Vega는 1% 기준이므로 % 입력
    theta_pnl = portfolio_greeks.net_theta * dt_days

    explained = delta_pnl + gamma_pnl + vega_pnl + theta_pnl
    residual = (actual_pnl - explained) if actual_pnl is not None else 0.0

    return PnLAttribution(
        total_pnl=actual_pnl if actual_pnl is not None else explained,
        delta_pnl=delta_pnl,
        gamma_pnl=gamma_pnl,
        vega_pnl=vega_pnl,
        theta_pnl=theta_pnl,
        residual=residual,
    )
