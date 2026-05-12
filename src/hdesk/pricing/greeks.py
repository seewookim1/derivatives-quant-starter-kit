"""Greeks 계산 - numpy 벡터화 + numba JIT 그리드"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy.stats import norm

from hdesk.pricing.black_scholes import bs_d1_d2


@dataclass
class GreeksResult:
    delta: np.ndarray
    gamma: np.ndarray
    vega: np.ndarray    # 1% vol 변화 기준
    theta: np.ndarray   # 1일 기준
    rho: np.ndarray     # 1% 금리 변화 기준
    vanna: np.ndarray   # dDelta/dVol
    volga: np.ndarray   # dVega/dVol (Vomma)


def compute_all_greeks(
    S: np.ndarray | float,
    K: np.ndarray | float,
    T: np.ndarray | float,
    r: np.ndarray | float,
    sigma: np.ndarray | float,
    option_type: np.ndarray | str,
    q: np.ndarray | float = 0.0,
) -> GreeksResult:
    """모든 1차/2차 Greeks 벡터화 계산."""
    S = np.asarray(S, dtype=float)
    K = np.asarray(K, dtype=float)
    T = np.asarray(T, dtype=float)
    r = np.asarray(r, dtype=float)
    sigma = np.asarray(sigma, dtype=float)
    q = np.asarray(q, dtype=float)

    T = np.where(T <= 0, 1e-10, T)
    sqrt_T = np.sqrt(T)

    d1, d2 = bs_d1_d2(S, K, T, r, sigma, q)
    nd1 = norm.cdf(d1)
    nd2 = norm.cdf(d2)
    nprime_d1 = norm.pdf(d1)

    discount_S = S * np.exp(-q * T)
    discount_K = K * np.exp(-r * T)

    is_call = np.asarray(option_type) == "C"
    call_sign = np.where(is_call, 1.0, -1.0)

    # Delta
    delta_call = np.exp(-q * T) * nd1
    delta_put = np.exp(-q * T) * (nd1 - 1.0)
    delta = np.where(is_call, delta_call, delta_put)

    # Gamma (call == put)
    gamma = np.exp(-q * T) * nprime_d1 / (S * sigma * sqrt_T)

    # Vega (1% vol 변화 기준, /100)
    vega = discount_S * nprime_d1 * sqrt_T / 100.0

    # Theta (일 기준)
    theta_common = -(discount_S * nprime_d1 * sigma) / (2.0 * sqrt_T)
    theta_call = theta_common - r * discount_K * nd2 + q * discount_S * nd1
    theta_put = theta_common + r * discount_K * norm.cdf(-d2) - q * discount_S * norm.cdf(-d1)
    theta = np.where(is_call, theta_call, theta_put) / 365.0

    # Rho (1% 금리 변화 기준, /100)
    rho_call = T * discount_K * nd2 / 100.0
    rho_put = -T * discount_K * norm.cdf(-d2) / 100.0
    rho = np.where(is_call, rho_call, rho_put)

    # Vanna = dDelta/dVol = -exp(-qT) * N'(d1) * d2 / sigma
    vanna = -np.exp(-q * T) * nprime_d1 * d2 / sigma

    # Volga (Vomma) = Vega * d1 * d2 / sigma
    volga = vega * d1 * d2 / sigma

    return GreeksResult(
        delta=delta,
        gamma=gamma,
        vega=vega,
        theta=theta,
        rho=rho,
        vanna=vanna,
        volga=volga,
    )


def greeks_grid(
    S_range: np.ndarray,
    K: float,
    T: float,
    r: float,
    sigma: float,
    option_type: str,
    q: float = 0.0,
) -> GreeksResult:
    """기초자산 가격 범위에 대한 Greeks 그리드 계산."""
    return compute_all_greeks(
        S=S_range,
        K=np.full_like(S_range, K),
        T=np.full_like(S_range, T),
        r=np.full_like(S_range, r),
        sigma=np.full_like(S_range, sigma),
        option_type=np.where(np.ones_like(S_range, dtype=bool), option_type, option_type),
        q=np.full_like(S_range, q),
    )
