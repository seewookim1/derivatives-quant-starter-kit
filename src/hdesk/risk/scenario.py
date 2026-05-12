"""시나리오 분석 - 스트레스 테스트"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

import numpy as np

if TYPE_CHECKING:
    from hdesk.data.models.position import Position
    from hdesk.pricing.vol_surface import VolSurface

# 사전 정의 시나리오 (spot_shock: 상대적 변화, vol_shock: 절대 변화)
SCENARIOS: dict[str, dict] = {
    "covid_crash": {
        "name": "COVID 급락 (2020.03)",
        "spot_shock": -0.35,
        "vol_shock": +0.50,
    },
    "black_monday": {
        "name": "블랙 먼데이 (1987.10)",
        "spot_shock": -0.22,
        "vol_shock": +0.40,
    },
    "vol_spike_20pct": {
        "name": "변동성 급등 +20%p",
        "spot_shock": 0.0,
        "vol_shock": +0.20,
    },
    "vol_crush_10pct": {
        "name": "변동성 급락 -10%p",
        "spot_shock": 0.0,
        "vol_shock": -0.10,
    },
    "spot_up_5pct": {
        "name": "기초자산 +5%",
        "spot_shock": +0.05,
        "vol_shock": -0.02,
    },
    "spot_down_10pct": {
        "name": "기초자산 -10%",
        "spot_shock": -0.10,
        "vol_shock": +0.05,
    },
    "flat": {
        "name": "현재 상태 (기준)",
        "spot_shock": 0.0,
        "vol_shock": 0.0,
    },
}


@dataclass
class ScenarioResult:
    scenario_name: str
    spot_shock: float
    vol_shock: float
    pnl: float           # 시나리오 P&L
    new_delta: float
    new_vega: float


def run_scenario(
    positions: list["Position"],
    spot_prices: dict[str, float],
    vol_surface: "VolSurface",
    scenario_key: str,
) -> ScenarioResult:
    """특정 시나리오에서의 포트폴리오 P&L 계산.

    Args:
        positions: 활성 포지션 목록
        spot_prices: {underlying: current_price}
        vol_surface: 현재 변동성 서피스
        scenario_key: SCENARIOS 키 값

    Returns:
        ScenarioResult
    """
    from hdesk.pricing.black_scholes import bs_price
    from hdesk.pricing.greeks import compute_all_greeks
    from hdesk.utils.config import get_settings

    scenario = SCENARIOS[scenario_key]
    spot_shock = scenario["spot_shock"]
    vol_shock = scenario["vol_shock"]

    settings = get_settings()
    r = settings.default_risk_free_rate

    total_pnl = 0.0
    new_delta = 0.0
    new_vega = 0.0

    for pos in positions:
        if pos.instrument_type != "OPTION" or pos.expiry is None or pos.strike is None:
            continue

        S0 = spot_prices.get(pos.underlying, 0.0)
        if S0 == 0:
            continue

        S_shocked = S0 * (1 + spot_shock)
        K = pos.strike
        T = (pos.expiry - __import__("datetime").date.today()).days / 365.0
        if T <= 0:
            continue

        sigma0 = vol_surface.get_vol(K, T)
        sigma_shocked = max(sigma0 + vol_shock, 0.001)

        # 현재 가격
        price_before = float(bs_price(S0, K, T, r, sigma0, pos.option_type or "C"))
        # 시나리오 가격
        price_after = float(bs_price(S_shocked, K, T, r, sigma_shocked, pos.option_type or "C"))

        pnl = (price_after - price_before) * pos.quantity * pos.multiplier
        total_pnl += pnl

        # 시나리오에서의 Greeks
        g = compute_all_greeks(
            S=np.array([S_shocked]),
            K=np.array([K]),
            T=np.array([T]),
            r=np.array([r]),
            sigma=np.array([sigma_shocked]),
            option_type=np.array([pos.option_type or "C"]),
        )
        new_delta += float(g.delta[0]) * pos.quantity * pos.multiplier
        new_vega += float(g.vega[0]) * pos.quantity * pos.multiplier

    return ScenarioResult(
        scenario_name=scenario["name"],
        spot_shock=spot_shock,
        vol_shock=vol_shock,
        pnl=total_pnl,
        new_delta=new_delta,
        new_vega=new_vega,
    )


def run_all_scenarios(
    positions: list["Position"],
    spot_prices: dict[str, float],
    vol_surface: "VolSurface",
) -> dict[str, ScenarioResult]:
    """모든 사전 정의 시나리오 실행."""
    return {
        key: run_scenario(positions, spot_prices, vol_surface, key)
        for key in SCENARIOS
    }
