"""Black-Scholes 수치 검증 테스트

참조값: Haug, E. (2007) "The Complete Guide to Option Pricing Formulas"
"""

from __future__ import annotations

import numpy as np
import pytest

from hdesk.pricing.black_scholes import bs_price


class TestBSPrice:
    def test_atm_call(self):
        """ATM 콜 옵션 기본 검증."""
        price = float(bs_price(S=100, K=100, T=1.0, r=0.05, sigma=0.20, option_type="C"))
        # 교재값 약 10.45
        assert 9.0 < price < 12.0

    def test_atm_put(self):
        """ATM 풋 옵션 기본 검증."""
        price = float(bs_price(S=100, K=100, T=1.0, r=0.05, sigma=0.20, option_type="P"))
        # 풋-콜 패리티: P = C - S + K*exp(-rT)
        call = float(bs_price(S=100, K=100, T=1.0, r=0.05, sigma=0.20, option_type="C"))
        parity_put = call - 100 + 100 * np.exp(-0.05)
        assert abs(price - parity_put) < 1e-6

    def test_put_call_parity(self, sample_option_params):
        """풋-콜 패리티 검증."""
        p = sample_option_params
        call = float(bs_price(**{**p, "option_type": "C"}))
        put = float(bs_price(**{**p, "option_type": "P"}))
        parity = call - put - p["S"] * np.exp(-p["q"] * p["T"]) + p["K"] * np.exp(-p["r"] * p["T"])
        assert abs(parity) < 1e-8

    def test_deep_itm_call(self):
        """Deep ITM 콜: 내재가치에 근접해야 함."""
        price = float(bs_price(S=200, K=100, T=0.01, r=0.0, sigma=0.01, option_type="C"))
        assert abs(price - 100.0) < 0.5

    def test_deep_otm_call_near_zero(self):
        """Deep OTM 콜: 거의 0에 가까워야 함."""
        price = float(bs_price(S=100, K=200, T=0.01, r=0.0, sigma=0.01, option_type="C"))
        assert price < 0.001

    def test_vectorized(self):
        """벡터화 입력 처리 검증."""
        S = np.array([100.0, 110.0, 90.0])
        K = np.array([100.0, 100.0, 100.0])
        prices = bs_price(S=S, K=K, T=0.5, r=0.05, sigma=0.20, option_type="C")
        assert prices.shape == (3,)
        assert all(prices > 0)
        assert prices[1] > prices[0] > prices[2]  # ITM > ATM > OTM

    def test_zero_expiry_intrinsic_value(self):
        """만기 = 0: 내재가치 반환."""
        call = float(bs_price(S=110, K=100, T=0, r=0.05, sigma=0.20, option_type="C"))
        assert call >= 10.0  # 최소 내재가치

    def test_haug_example(self):
        """Haug 교재 예제: S=60, K=65, T=0.25, r=0.08, sigma=0.30, C≈2.1334."""
        price = float(bs_price(S=60, K=65, T=0.25, r=0.08, sigma=0.30, option_type="C"))
        assert abs(price - 2.1334) < 0.02
