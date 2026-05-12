"""아메리칸 옵션 프라이싱 - QuantLib 바인딩"""

from __future__ import annotations

import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class AmericanResult:
    price: float
    delta: float
    gamma: float
    theta: float


def american_binomial(
    S: float,
    K: float,
    T: float,
    r: float,
    sigma: float,
    option_type: str,
    q: float = 0.0,
    steps: int = 200,
) -> AmericanResult:
    """이항 트리(CRR) 방식 아메리칸 옵션 프라이싱.

    Args:
        S: 기초자산 현재가
        K: 행사가
        T: 잔존 만기 (연수)
        r: 무위험 이자율
        sigma: 변동성
        option_type: 'C' 또는 'P'
        q: 배당 수익률
        steps: 이항 트리 단계 수

    Returns:
        AmericanResult (price, delta, gamma, theta)
    """
    import QuantLib as ql

    today = ql.Date.todaysDate()
    ql.Settings.instance().evaluationDate = today
    expiry = today + ql.Period(int(T * 365), ql.Days)

    payoff = ql.PlainVanillaPayoff(
        ql.Option.Call if option_type == "C" else ql.Option.Put, K
    )
    exercise = ql.AmericanExercise(today, expiry)
    option = ql.VanillaOption(payoff, exercise)

    spot = ql.SimpleQuote(S)
    rts = ql.YieldTermStructureHandle(
        ql.FlatForward(today, ql.QuoteHandle(ql.SimpleQuote(r)), ql.Actual365Fixed())
    )
    divts = ql.YieldTermStructureHandle(
        ql.FlatForward(today, ql.QuoteHandle(ql.SimpleQuote(q)), ql.Actual365Fixed())
    )
    volts = ql.BlackVolTermStructureHandle(
        ql.BlackConstantVol(
            today, ql.NullCalendar(), ql.QuoteHandle(ql.SimpleQuote(sigma)), ql.Actual365Fixed()
        )
    )

    process = ql.BlackScholesMertonProcess(ql.QuoteHandle(spot), divts, rts, volts)
    engine = ql.BinomialVanillaEngine(process, "crr", steps)
    option.setPricingEngine(engine)

    return AmericanResult(
        price=option.NPV(),
        delta=option.delta(),
        gamma=option.gamma(),
        theta=option.theta() / 365.0,
    )
