"""리스크 한도 모니터링"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from hdesk.risk.greeks_agg import PortfolioGreeks


@dataclass
class LimitBreachEvent:
    metric: str
    current_value: float
    limit_value: float
    utilization_pct: float
    is_breach: bool

    def to_dict(self) -> dict:
        return {
            "metric": self.metric,
            "current_value": self.current_value,
            "limit_value": self.limit_value,
            "utilization_pct": round(self.utilization_pct, 1),
            "is_breach": self.is_breach,
        }


def check_limits(
    portfolio_greeks: "PortfolioGreeks",
    limits: dict[str, float] | None = None,
) -> list[LimitBreachEvent]:
    """포트폴리오 Greeks 한도 점검.

    Args:
        portfolio_greeks: 포트폴리오 집계 Greeks
        limits: 한도 딕셔너리 (None이면 config 기본값 사용)

    Returns:
        LimitBreachEvent 목록
    """
    from hdesk.utils.config import get_settings

    settings = get_settings()
    if limits is None:
        limits = {
            "net_delta": settings.risk_limit_net_delta,
            "net_vega": settings.risk_limit_net_vega,
        }

    events = []

    checks = {
        "net_delta": abs(portfolio_greeks.net_delta),
        "net_vega": abs(portfolio_greeks.net_vega),
    }

    for metric, current in checks.items():
        limit = limits.get(metric)
        if limit is None:
            continue
        utilization = (current / limit * 100) if limit != 0 else 0.0
        events.append(
            LimitBreachEvent(
                metric=metric,
                current_value=current,
                limit_value=limit,
                utilization_pct=utilization,
                is_breach=current > limit,
            )
        )

    return events
