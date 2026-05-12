"""pytest fixtures"""

from __future__ import annotations

import pytest
import numpy as np


@pytest.fixture
def sample_option_params():
    """표준 BS 파라미터 세트 (KOSPI200 ATM 콜)."""
    return {
        "S": 350.0,
        "K": 350.0,
        "T": 30 / 365.0,
        "r": 0.035,
        "sigma": 0.20,
        "option_type": "C",
        "q": 0.0,
    }


@pytest.fixture
def vol_surface_data():
    """샘플 변동성 서피스 데이터."""
    strikes = np.array([300.0, 320.0, 340.0, 350.0, 360.0, 380.0, 400.0])
    expiries = np.array([1 / 12, 2 / 12, 3 / 12, 6 / 12, 1.0])
    # 스큐 포함 변동성 (OTM 풋이 ITM 콜보다 높은 변동성)
    vols = np.array([
        [0.28, 0.25, 0.22, 0.20, 0.19, 0.18, 0.17],
        [0.27, 0.24, 0.21, 0.20, 0.19, 0.18, 0.17],
        [0.26, 0.23, 0.21, 0.20, 0.19, 0.18, 0.17],
        [0.25, 0.23, 0.21, 0.20, 0.19, 0.19, 0.18],
        [0.24, 0.22, 0.20, 0.19, 0.19, 0.19, 0.18],
    ])
    return {"strikes": strikes, "expiries": expiries, "vols": vols}
