"""변동성 서피스 보간 검증 테스트"""

from __future__ import annotations

import numpy as np
import pytest

from hdesk.pricing.vol_surface import VolSurface


class TestVolSurface:
    def test_flat_surface(self):
        """플랫 서피스 생성 및 단일점 조회."""
        surface = VolSurface.flat(0.20)
        vol = surface.get_vol(K=1.0, T=0.5)
        assert abs(vol - 0.20) < 0.01

    def test_grid_points_exact(self, vol_surface_data):
        """격자점에서의 보간값 = 입력값 (스플라인 보간 허용 오차)."""
        surface = VolSurface(**vol_surface_data)
        # ATM (K=350, T=1/12)에서의 변동성
        vol = surface.get_vol(K=350.0, T=1 / 12)
        assert abs(vol - 0.20) < 0.02

    def test_boundary_clamping(self, vol_surface_data):
        """경계 밖 요청 → 클램핑 처리 (예외 없음)."""
        surface = VolSurface(**vol_surface_data)
        # 격자 밖 행사가
        vol_low = surface.get_vol(K=200.0, T=0.5)
        vol_high = surface.get_vol(K=600.0, T=0.5)
        assert vol_low > 0
        assert vol_high > 0

    def test_no_negative_vol(self, vol_surface_data):
        """보간된 변동성은 항상 양수."""
        surface = VolSurface(**vol_surface_data)
        strikes = np.linspace(250, 450, 50)
        expiries = np.linspace(0.05, 1.5, 10)
        for T in expiries:
            for K in strikes:
                vol = surface.get_vol(K, T)
                assert vol > 0, f"음수 변동성: K={K}, T={T:.2f}, vol={vol}"

    def test_json_serialization(self, vol_surface_data):
        """JSON 직렬화 → 역직렬화 후 동일한 값."""
        original = VolSurface(**vol_surface_data)
        json_str = original.to_json()
        restored = VolSurface.from_json(json_str)
        assert abs(original.get_vol(350.0, 0.5) - restored.get_vol(350.0, 0.5)) < 1e-8

    def test_vectorized_output_shape(self, vol_surface_data):
        """벡터화 조회 - 출력 형태 검증."""
        surface = VolSurface(**vol_surface_data)
        K = np.array([320.0, 340.0, 350.0, 360.0, 380.0])
        T = np.full(5, 0.25)
        vols = surface.get_vol_vectorized(K, T)
        assert vols.shape == (5,)
        assert all(vols > 0)

    def test_skew_direction(self, vol_surface_data):
        """OTM 풋(낮은 행사가)이 ATM보다 높은 변동성을 가져야 함 (스큐)."""
        surface = VolSurface(**vol_surface_data)
        T = 0.25
        vol_otm_put = surface.get_vol(K=310.0, T=T)
        vol_atm = surface.get_vol(K=350.0, T=T)
        assert vol_otm_put > vol_atm
