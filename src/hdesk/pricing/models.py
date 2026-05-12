"""확률 변동성 모델 - Heston, SABR (QuantLib 기반)"""

from __future__ import annotations

import logging
from dataclasses import dataclass

import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class HestonParams:
    """Heston 모델 파라미터.

    dS = (r-q)S dt + sqrt(v) S dW_S
    dv = kappa*(theta-v) dt + sigma_v*sqrt(v) dW_v
    corr(dW_S, dW_v) = rho
    """

    v0: float     # 초기 분산
    kappa: float  # 평균 회귀 속도
    theta: float  # 장기 평균 분산
    sigma_v: float  # 변동성의 변동성 (vol-of-vol)
    rho: float    # 브라운 운동 상관계수


def heston_price(
    S: float,
    K: float,
    T: float,
    r: float,
    q: float,
    params: HestonParams,
    option_type: str,
) -> float:
    """Heston 모델 유러피안 옵션 가격."""
    import QuantLib as ql

    today = ql.Date.todaysDate()
    ql.Settings.instance().evaluationDate = today
    expiry = today + ql.Period(int(T * 365), ql.Days)

    payoff = ql.PlainVanillaPayoff(
        ql.Option.Call if option_type == "C" else ql.Option.Put, K
    )
    option = ql.VanillaOption(payoff, ql.EuropeanExercise(expiry))

    spot = ql.QuoteHandle(ql.SimpleQuote(S))
    rts = ql.YieldTermStructureHandle(
        ql.FlatForward(today, r, ql.Actual365Fixed())
    )
    divts = ql.YieldTermStructureHandle(
        ql.FlatForward(today, q, ql.Actual365Fixed())
    )

    process = ql.HestonProcess(
        rts, divts, spot,
        params.v0, params.kappa, params.theta, params.sigma_v, params.rho
    )
    model = ql.HestonModel(process)
    engine = ql.AnalyticHestonEngine(model)
    option.setPricingEngine(engine)

    return option.NPV()


def calibrate_heston(
    S: float,
    r: float,
    q: float,
    market_vols: np.ndarray,
    strikes: np.ndarray,
    expiries: np.ndarray,
) -> HestonParams:
    """시장 IV 데이터로 Heston 모델 캘리브레이션.

    Args:
        market_vols: 시장 내재 변동성 행렬 [n_expiries x n_strikes]
        strikes: 행사가 배열
        expiries: 잔존 만기 배열 (연수)

    Returns:
        캘리브레이션된 HestonParams
    """
    import QuantLib as ql

    today = ql.Date.todaysDate()
    ql.Settings.instance().evaluationDate = today

    rts = ql.YieldTermStructureHandle(
        ql.FlatForward(today, r, ql.Actual365Fixed())
    )
    divts = ql.YieldTermStructureHandle(
        ql.FlatForward(today, q, ql.Actual365Fixed())
    )
    spot = ql.QuoteHandle(ql.SimpleQuote(S))

    # 시장 데이터 핼퍼 생성
    helpers = []
    for i, T in enumerate(expiries):
        expiry_date = today + ql.Period(int(T * 365), ql.Days)
        for j, K in enumerate(strikes):
            vol = market_vols[i, j]
            helper = ql.HestonModelHelper(
                ql.Period(int(T * 365), ql.Days),
                ql.NullCalendar(),
                S,
                K,
                ql.QuoteHandle(ql.SimpleQuote(vol)),
                rts,
                divts,
            )
            helpers.append(helper)

    # 초기 파라미터 설정
    process = ql.HestonProcess(rts, divts, spot, 0.1, 1.0, 0.1, 0.5, -0.5)
    model = ql.HestonModel(process)

    # Levenberg-Marquardt 최적화
    engine = ql.AnalyticHestonEngine(model)
    for h in helpers:
        h.setPricingEngine(engine)

    optimizer = ql.LevenbergMarquardt(1e-8, 1e-8, 1e-8)
    model.calibrate(helpers, optimizer, ql.EndCriteria(500, 50, 1e-8, 1e-8, 1e-8))

    params = model.params()
    return HestonParams(
        v0=params[0],
        kappa=params[1],
        theta=params[2],
        sigma_v=params[3],
        rho=params[4],
    )
