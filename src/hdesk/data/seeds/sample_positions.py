"""테스트용 샘플 포지션 데이터"""

from __future__ import annotations

from datetime import date

from hdesk.data.models.position import Position, Trade


def get_sample_positions() -> list[Position]:
    """KOSPI200 옵션/선물 샘플 포지션."""
    return [
        # KOSPI200 ATM 콜 매수
        Position(
            underlying="KOSPI200",
            instrument_type="OPTION",
            option_type="C",
            strike=350.0,
            expiry=date(2025, 6, 12),
            quantity=10,
            multiplier=250_000,
            avg_price=5.50,
        ),
        # KOSPI200 OTM 풋 매수 (헤지)
        Position(
            underlying="KOSPI200",
            instrument_type="OPTION",
            option_type="P",
            strike=330.0,
            expiry=date(2025, 6, 12),
            quantity=20,
            multiplier=250_000,
            avg_price=3.20,
        ),
        # KOSPI200 선물 매도 (델타 헤지)
        Position(
            underlying="KOSPI200",
            instrument_type="FUTURE",
            option_type=None,
            strike=None,
            expiry=date(2025, 6, 12),
            quantity=-3,
            multiplier=250_000,
            avg_price=352.50,
        ),
        # 삼성전자 콜 매도
        Position(
            underlying="005930 KS",
            instrument_type="OPTION",
            option_type="C",
            strike=80_000.0,
            expiry=date(2025, 6, 27),
            quantity=-5,
            multiplier=10,
            avg_price=1_200.0,
        ),
    ]
