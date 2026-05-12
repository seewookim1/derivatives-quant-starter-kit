"""포트폴리오 Greeks 집계 및 버킷팅"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from hdesk.data.models.position import Position
    from hdesk.pricing.greeks import GreeksResult


@dataclass
class PortfolioGreeks:
    """포트폴리오 단위 집계 Greeks."""

    net_delta: float = 0.0           # 주식 수량 환산 델타 합계
    net_gamma: float = 0.0           # 감마 합계 (1포인트 이동시 델타 변화)
    net_vega: float = 0.0            # 베가 합계 (1% vol 변화시 P&L)
    net_theta: float = 0.0           # 일 theta 합계
    net_rho: float = 0.0

    delta_by_underlying: dict[str, float] = field(default_factory=dict)
    vega_by_expiry: dict[str, float] = field(default_factory=dict)
    gamma_by_underlying: dict[str, float] = field(default_factory=dict)

    position_count: int = 0

    def to_dict(self) -> dict:
        return {
            "net_delta": self.net_delta,
            "net_gamma": self.net_gamma,
            "net_vega": self.net_vega,
            "net_theta": self.net_theta,
            "net_rho": self.net_rho,
            "delta_by_underlying": self.delta_by_underlying,
            "vega_by_expiry": self.vega_by_expiry,
            "gamma_by_underlying": self.gamma_by_underlying,
            "position_count": self.position_count,
        }


def aggregate_portfolio_greeks(
    positions: list["Position"],
    greeks_by_position: dict[int, "GreeksResult"],
) -> PortfolioGreeks:
    """포지션별 Greeks를 포트폴리오 단위로 집계.

    Args:
        positions: 활성 포지션 목록
        greeks_by_position: {position_id: GreeksResult}

    Returns:
        포트폴리오 집계 Greeks
    """
    portfolio = PortfolioGreeks(position_count=len(positions))

    for pos in positions:
        if pos.id not in greeks_by_position:
            continue

        g = greeks_by_position[pos.id]
        qty = pos.quantity
        mult = pos.multiplier

        # 델타: 계약수 x 멀티플라이어 x 델타
        delta_contrib = float(np.squeeze(g.delta)) * qty * mult
        gamma_contrib = float(np.squeeze(g.gamma)) * qty * mult
        vega_contrib = float(np.squeeze(g.vega)) * qty * mult
        theta_contrib = float(np.squeeze(g.theta)) * qty * mult
        rho_contrib = float(np.squeeze(g.rho)) * qty * mult

        portfolio.net_delta += delta_contrib
        portfolio.net_gamma += gamma_contrib
        portfolio.net_vega += vega_contrib
        portfolio.net_theta += theta_contrib
        portfolio.net_rho += rho_contrib

        # 기초자산별 집계
        und = pos.underlying
        portfolio.delta_by_underlying[und] = (
            portfolio.delta_by_underlying.get(und, 0.0) + delta_contrib
        )
        portfolio.gamma_by_underlying[und] = (
            portfolio.gamma_by_underlying.get(und, 0.0) + gamma_contrib
        )

        # 만기별 베가 버킷
        if pos.expiry is not None:
            expiry_label = pos.expiry.strftime("%Y-%m")
            portfolio.vega_by_expiry[expiry_label] = (
                portfolio.vega_by_expiry.get(expiry_label, 0.0) + vega_contrib
            )

    return portfolio
