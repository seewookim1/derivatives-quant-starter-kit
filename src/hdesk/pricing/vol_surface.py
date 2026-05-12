"""변동성 서피스 - RectBivariateSpline 보간 + Redis 캐시 직렬화"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field

import numpy as np
from scipy.interpolate import RectBivariateSpline

logger = logging.getLogger(__name__)


@dataclass
class VolSurface:
    """변동성 서피스 (만기 x 행사가 격자).

    Attributes:
        strikes: 행사가 배열 (오름차순)
        expiries: 잔존 만기 배열 (연수, 오름차순)
        vols: 변동성 행렬 [n_expiries x n_strikes]
        underlying: 기초자산 심볼
    """

    strikes: np.ndarray
    expiries: np.ndarray
    vols: np.ndarray
    underlying: str = ""
    _spline: RectBivariateSpline = field(init=False, repr=False)

    def __post_init__(self) -> None:
        self.strikes = np.asarray(self.strikes, dtype=float)
        self.expiries = np.asarray(self.expiries, dtype=float)
        self.vols = np.asarray(self.vols, dtype=float)
        self._fit()

    def _fit(self) -> None:
        """스플라인 재보정."""
        if self.vols.shape != (len(self.expiries), len(self.strikes)):
            raise ValueError(
                f"vols 형태 불일치: {self.vols.shape} != "
                f"({len(self.expiries)}, {len(self.strikes)})"
            )
        # kx, ky=3 (cubic spline), 최소 4개 격자점 필요
        kx = min(3, len(self.expiries) - 1)
        ky = min(3, len(self.strikes) - 1)
        self._spline = RectBivariateSpline(
            self.expiries, self.strikes, self.vols, kx=kx, ky=ky
        )

    def get_vol(self, K: float, T: float) -> float:
        """단일 (K, T) 변동성 조회 (경계 클램핑)."""
        T_clamped = float(np.clip(T, self.expiries[0], self.expiries[-1]))
        K_clamped = float(np.clip(K, self.strikes[0], self.strikes[-1]))
        vol = float(self._spline(T_clamped, K_clamped))
        return max(vol, 1e-4)  # 음수 변동성 방지

    def get_vol_vectorized(self, K: np.ndarray, T: np.ndarray) -> np.ndarray:
        """벡터화된 변동성 조회."""
        T = np.clip(T, self.expiries[0], self.expiries[-1])
        K = np.clip(K, self.strikes[0], self.strikes[-1])
        vols = np.array([
            float(self._spline(t, k)) for t, k in zip(T, K)
        ])
        return np.maximum(vols, 1e-4)

    def to_dict(self) -> dict:
        """Redis 저장용 JSON 직렬화."""
        return {
            "underlying": self.underlying,
            "strikes": self.strikes.tolist(),
            "expiries": self.expiries.tolist(),
            "vols": self.vols.tolist(),
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: dict) -> "VolSurface":
        return cls(
            strikes=np.array(data["strikes"]),
            expiries=np.array(data["expiries"]),
            vols=np.array(data["vols"]),
            underlying=data.get("underlying", ""),
        )

    @classmethod
    def from_json(cls, json_str: str) -> "VolSurface":
        return cls.from_dict(json.loads(json_str))

    @classmethod
    def flat(cls, vol: float, underlying: str = "") -> "VolSurface":
        """테스트용 플랫 변동성 서피스 생성."""
        expiries = np.array([1 / 12, 3 / 12, 6 / 12, 1.0, 2.0])
        strikes = np.array([0.8, 0.9, 0.95, 1.0, 1.05, 1.1, 1.2])
        vols = np.full((len(expiries), len(strikes)), vol)
        return cls(strikes=strikes, expiries=expiries, vols=vols, underlying=underlying)
