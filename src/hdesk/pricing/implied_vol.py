"""내재 변동성(Implied Volatility) 역산 - 멀티 방법론"""

from __future__ import annotations

import logging

import numpy as np
from scipy.optimize import brentq

logger = logging.getLogger(__name__)

# IV 탐색 경계
_IV_LB = 1e-6
_IV_UB = 10.0


def implied_vol(
    market_price: float,
    S: float,
    K: float,
    T: float,
    r: float,
    option_type: str,
    q: float = 0.0,
    method: str = "vollib",
) -> float:
    """내재 변동성 역산.

    Args:
        market_price: 시장 옵션 가격
        S: 기초자산 현재가
        K: 행사가
        T: 잔존 만기 (연수)
        r: 무위험 이자율
        option_type: 'C' 또는 'P'
        q: 배당 수익률
        method: 'vollib' (실시간 빠름) | 'quantlib' (정밀) | 'scipy' (fallback)

    Returns:
        내재 변동성 (연율, 예: 0.20 = 20%)

    Raises:
        ValueError: IV 수렴 실패 시
    """
    if T <= 0:
        raise ValueError(f"잔존 만기가 0 이하: T={T}")

    if method == "vollib":
        return _iv_vollib(market_price, S, K, T, r, option_type, q)
    elif method == "quantlib":
        return _iv_quantlib(market_price, S, K, T, r, option_type, q)
    else:
        return _iv_scipy(market_price, S, K, T, r, option_type, q)


def implied_vol_vectorized(
    market_prices: np.ndarray,
    S: np.ndarray,
    K: np.ndarray,
    T: np.ndarray,
    r: float,
    option_types: np.ndarray,
    q: float = 0.0,
    method: str = "vollib",
) -> np.ndarray:
    """배열 단위 내재 변동성 역산."""
    result = np.full(len(market_prices), np.nan)
    for i in range(len(market_prices)):
        try:
            result[i] = implied_vol(
                market_prices[i], S[i], K[i], T[i], r, option_types[i], q, method
            )
        except Exception:
            result[i] = np.nan
    return result


def _iv_vollib(
    market_price: float,
    S: float,
    K: float,
    T: float,
    r: float,
    option_type: str,
    q: float,
) -> float:
    try:
        from py_vollib.black_scholes_merton.implied_volatility import implied_volatility

        flag = "c" if option_type == "C" else "p"
        return implied_volatility(market_price, S, K, T, r, q, flag)
    except ImportError:
        logger.warning("py_vollib 미설치, scipy fallback 사용")
        return _iv_scipy(market_price, S, K, T, r, option_type, q)
    except Exception as e:
        logger.debug("vollib IV 실패 (%s), scipy fallback: %s", type(e).__name__, e)
        return _iv_scipy(market_price, S, K, T, r, option_type, q)


def _iv_quantlib(
    market_price: float,
    S: float,
    K: float,
    T: float,
    r: float,
    option_type: str,
    q: float,
) -> float:
    try:
        import QuantLib as ql

        today = ql.Date.todaysDate()
        ql.Settings.instance().evaluationDate = today

        expiry = today + ql.Period(int(T * 365), ql.Days)
        payoff = ql.PlainVanillaPayoff(
            ql.Option.Call if option_type == "C" else ql.Option.Put, K
        )
        exercise = ql.EuropeanExercise(expiry)
        option = ql.VanillaOption(payoff, exercise)

        spot = ql.SimpleQuote(S)
        rate = ql.SimpleQuote(r)
        div = ql.SimpleQuote(q)
        vol_quote = ql.SimpleQuote(0.20)

        rts = ql.YieldTermStructureHandle(
            ql.FlatForward(today, ql.QuoteHandle(rate), ql.Actual365Fixed())
        )
        divts = ql.YieldTermStructureHandle(
            ql.FlatForward(today, ql.QuoteHandle(div), ql.Actual365Fixed())
        )
        volts = ql.BlackVolTermStructureHandle(
            ql.BlackConstantVol(today, ql.NullCalendar(), ql.QuoteHandle(vol_quote), ql.Actual365Fixed())
        )

        process = ql.BlackScholesMertonProcess(
            ql.QuoteHandle(spot), divts, rts, volts
        )
        engine = ql.AnalyticEuropeanEngine(process)
        option.setPricingEngine(engine)

        return option.impliedVolatility(market_price, process)
    except ImportError:
        logger.warning("QuantLib 미설치, scipy fallback 사용")
        return _iv_scipy(market_price, S, K, T, r, option_type, q)
    except Exception as e:
        logger.debug("QuantLib IV 실패 (%s), scipy fallback: %s", type(e).__name__, e)
        return _iv_scipy(market_price, S, K, T, r, option_type, q)


def _iv_scipy(
    market_price: float,
    S: float,
    K: float,
    T: float,
    r: float,
    option_type: str,
    q: float,
) -> float:
    from hdesk.pricing.black_scholes import bs_price

    def objective(sigma: float) -> float:
        return float(bs_price(S, K, T, r, sigma, option_type, q)) - market_price

    try:
        return brentq(objective, _IV_LB, _IV_UB, xtol=1e-8, maxiter=100)
    except ValueError as e:
        raise ValueError(f"IV 수렴 실패: S={S}, K={K}, T={T:.4f}, price={market_price:.4f}") from e
