"""VaR 계산 검증 테스트"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from hdesk.risk.var import VaRResult, historical_var


class TestHistoricalVaR:
    @pytest.fixture
    def normal_returns(self):
        """정규 분포 수익률 (표준화된 테스트 데이터)."""
        np.random.seed(42)
        return pd.Series(np.random.normal(0, 0.01, 500))

    def test_basic_var(self, normal_returns):
        """기본 VaR 계산 - 반환 타입 및 양수 검증."""
        result = historical_var(normal_returns, confidence=0.99, horizon_days=1)
        assert isinstance(result, VaRResult)
        assert result.var_amount > 0
        assert result.cvar_amount >= result.var_amount
        assert result.confidence == 0.99
        assert result.method == "historical"

    def test_var_increases_with_confidence(self, normal_returns):
        """신뢰수준 높을수록 VaR 증가."""
        r95 = historical_var(normal_returns, confidence=0.95)
        r99 = historical_var(normal_returns, confidence=0.99)
        assert r99.var_amount >= r95.var_amount

    def test_var_scales_with_horizon(self, normal_returns):
        """보유 기간 증가 시 VaR 증가 (sqrt-of-time 규칙)."""
        r1 = historical_var(normal_returns, confidence=0.99, horizon_days=1)
        r5 = historical_var(normal_returns, confidence=0.99, horizon_days=5)
        # 5일 VaR ≈ 1일 VaR * sqrt(5)
        ratio = r5.var_amount / r1.var_amount
        assert 1.5 < ratio < 3.5  # sqrt(5) ≈ 2.24

    def test_insufficient_data(self):
        """데이터 부족 시 예외 발생."""
        with pytest.raises(ValueError, match="데이터 부족"):
            historical_var(pd.Series([0.01, -0.01, 0.005]))

    def test_cvar_greater_than_var(self, normal_returns):
        """CVaR >= VaR."""
        result = historical_var(normal_returns, confidence=0.99)
        assert result.cvar_amount >= result.var_amount
