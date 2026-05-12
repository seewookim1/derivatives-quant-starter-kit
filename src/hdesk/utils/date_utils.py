"""영업일 및 만기일 유틸리티"""

from __future__ import annotations

from datetime import date, datetime, timedelta


# 한국 공휴일 (간소화 버전 - 실무에서는 holidays 패키지 사용 권장)
def is_business_day(d: date) -> bool:
    """영업일 여부 확인 (주말 제외)."""
    return d.weekday() < 5  # 0=월, 4=금


def next_business_day(d: date) -> date:
    """다음 영업일."""
    d = d + timedelta(days=1)
    while not is_business_day(d):
        d = d + timedelta(days=1)
    return d


def prev_business_day(d: date) -> date:
    """이전 영업일."""
    d = d - timedelta(days=1)
    while not is_business_day(d):
        d = d - timedelta(days=1)
    return d


def business_days_between(start: date, end: date) -> int:
    """두 날짜 사이의 영업일 수."""
    count = 0
    current = start
    while current < end:
        if is_business_day(current):
            count += 1
        current += timedelta(days=1)
    return count


def years_to_expiry(expiry: date, today: date | None = None) -> float:
    """만기까지 잔존 기간 (연수).

    Args:
        expiry: 만기일
        today: 기준일 (None이면 오늘)

    Returns:
        잔존 만기 (연수, Actual/365 방식)
    """
    if today is None:
        today = date.today()
    delta = (expiry - today).days
    return max(delta / 365.0, 0.0)


def kospi200_expiry(year: int, month: int) -> date:
    """KOSPI200 옵션/선물 만기일 계산.

    규칙: 매월 두 번째 목요일
    """
    d = date(year, month, 1)
    # 첫 번째 목요일 찾기
    days_until_thu = (3 - d.weekday()) % 7
    first_thu = d + timedelta(days=days_until_thu)
    # 두 번째 목요일
    return first_thu + timedelta(weeks=1)


def nearest_expiry(reference: date | None = None) -> date:
    """가장 가까운 KOSPI200 만기일."""
    if reference is None:
        reference = date.today()
    expiry = kospi200_expiry(reference.year, reference.month)
    if expiry <= reference:
        # 다음 달 만기
        if reference.month == 12:
            expiry = kospi200_expiry(reference.year + 1, 1)
        else:
            expiry = kospi200_expiry(reference.year, reference.month + 1)
    return expiry


def format_expiry_label(expiry: date) -> str:
    """만기일을 레이블 문자열로 변환. 예: '2025-03'"""
    return expiry.strftime("%Y-%m")
