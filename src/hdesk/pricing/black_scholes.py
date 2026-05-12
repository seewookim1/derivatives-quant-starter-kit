"""Black-Scholes 옵션 프라이싱 - 벡터화 numpy 구현"""

from __future__ import annotations

import numpy as np
from scipy.stats import norm


def bs_price(
    S: np.ndarray | float,
    K: np.ndarray | float,
    T: np.ndarray | float,
    r: np.ndarray | float,
    sigma: np.ndarray | float,
    option_type: np.ndarray | str,
    q: np.ndarray | float = 0.0,
) -> np.ndarray:
    """Black-Scholes 옵션 가격 계산 (벡터화).

    Args:
        S: 기초자산 현재가
        K: 행사가
        T: 잔존 만기 (연수, 예: 30일 = 30/365)
        r: 무위험 이자율 (연율, 예: 0.035)
        sigma: 변동성 (연율, 예: 0.20)
        option_type: 'C' 또는 'P' (배열 가능)
        q: 배당 수익률 (연율, 기본 0.0)

    Returns:
        옵션 이론가 배열
    """
    S = np.asarray(S, dtype=float)
    K = np.asarray(K, dtype=float)
    T = np.asarray(T, dtype=float)
    r = np.asarray(r, dtype=float)
    sigma = np.asarray(sigma, dtype=float)
    q = np.asarray(q, dtype=float)

    # T=0 처리: 내재가치 반환
    T = np.where(T <= 0, 1e-10, T)

    sqrt_T = np.sqrt(T)
    d1 = (np.log(S / K) + (r - q + 0.5 * sigma**2) * T) / (sigma * sqrt_T)
    d2 = d1 - sigma * sqrt_T

    discount_K = K * np.exp(-r * T)
    discount_S = S * np.exp(-q * T)

    call = discount_S * norm.cdf(d1) - discount_K * norm.cdf(d2)
    put = discount_K * norm.cdf(-d2) - discount_S * norm.cdf(-d1)

    is_call = np.asarray(option_type) == "C"
    return np.where(is_call, call, put)


def bs_d1_d2(
    S: np.ndarray,
    K: np.ndarray,
    T: np.ndarray,
    r: np.ndarray,
    sigma: np.ndarray,
    q: np.ndarray = 0.0,
) -> tuple[np.ndarray, np.ndarray]:
    """d1, d2 계산 (Greeks 계산 공통 사용)."""
    T = np.where(T <= 0, 1e-10, T)
    sqrt_T = np.sqrt(T)
    d1 = (np.log(S / K) + (r - q + 0.5 * sigma**2) * T) / (sigma * sqrt_T)
    d2 = d1 - sigma * sqrt_T
    return d1, d2
