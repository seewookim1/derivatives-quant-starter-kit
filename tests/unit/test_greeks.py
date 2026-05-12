"""Greeks 수치 검증 테스트"""

from __future__ import annotations

import numpy as np
import pytest

from hdesk.pricing.black_scholes import bs_price
from hdesk.pricing.greeks import compute_all_greeks


class TestGreeks:
    def test_delta_call_range(self, sample_option_params):
        """콜 델타 범위: [0, 1]."""
        p = sample_option_params
        g = compute_all_greeks(**p)
        assert 0.0 <= float(g.delta) <= 1.0

    def test_delta_put_range(self, sample_option_params):
        """풋 델타 범위: [-1, 0]."""
        p = {**sample_option_params, "option_type": "P"}
        g = compute_all_greeks(**p)
        assert -1.0 <= float(g.delta) <= 0.0

    def test_delta_put_call_relationship(self, sample_option_params):
        """Delta_call - Delta_put = exp(-qT)."""
        p = sample_option_params
        g_call = compute_all_greeks(**p)
        g_put = compute_all_greeks(**{**p, "option_type": "P"})
        expected = np.exp(-p["q"] * p["T"])
        assert abs(float(g_call.delta) - float(g_put.delta) - expected) < 1e-8

    def test_gamma_positive(self, sample_option_params):
        """Gamma는 항상 양수."""
        g = compute_all_greeks(**sample_option_params)
        assert float(g.gamma) > 0

    def test_gamma_symmetric_call_put(self, sample_option_params):
        """Gamma(call) == Gamma(put)."""
        g_call = compute_all_greeks(**sample_option_params)
        g_put = compute_all_greeks(**{**sample_option_params, "option_type": "P"})
        assert abs(float(g_call.gamma) - float(g_put.gamma)) < 1e-10

    def test_vega_positive(self, sample_option_params):
        """Vega는 항상 양수."""
        g = compute_all_greeks(**sample_option_params)
        assert float(g.vega) > 0

    def test_theta_negative_call(self, sample_option_params):
        """Theta(call)는 일반적으로 음수 (시간 감쇠)."""
        g = compute_all_greeks(**sample_option_params)
        assert float(g.theta) < 0

    def test_delta_numerical_consistency(self, sample_option_params):
        """Delta ≈ (C(S+h) - C(S-h)) / (2h) 수치 미분 검증."""
        p = sample_option_params
        h = 0.01
        price_up = float(bs_price(p["S"] + h, p["K"], p["T"], p["r"], p["sigma"], p["option_type"]))
        price_dn = float(bs_price(p["S"] - h, p["K"], p["T"], p["r"], p["sigma"], p["option_type"]))
        numerical_delta = (price_up - price_dn) / (2 * h)

        g = compute_all_greeks(**p)
        assert abs(float(g.delta) - numerical_delta) < 1e-4

    def test_gamma_numerical_consistency(self, sample_option_params):
        """Gamma ≈ (C(S+h) - 2C(S) + C(S-h)) / h² 수치 미분 검증."""
        p = sample_option_params
        h = 0.5
        price_up = float(bs_price(p["S"] + h, p["K"], p["T"], p["r"], p["sigma"], p["option_type"]))
        price_mid = float(bs_price(p["S"], p["K"], p["T"], p["r"], p["sigma"], p["option_type"]))
        price_dn = float(bs_price(p["S"] - h, p["K"], p["T"], p["r"], p["sigma"], p["option_type"]))
        numerical_gamma = (price_up - 2 * price_mid + price_dn) / h**2

        g = compute_all_greeks(**p)
        assert abs(float(g.gamma) - numerical_gamma) < 1e-4

    def test_atm_delta_approximately_half(self, sample_option_params):
        """ATM 콜 델타 ≈ 0.5 (정확히는 N(d1) > 0.5)."""
        g = compute_all_greeks(**sample_option_params)
        assert 0.4 < float(g.delta) < 0.7
