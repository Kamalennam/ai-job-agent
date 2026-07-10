from datetime import datetime

from app.utils.datetime_utils import ensure_utc, utc_now


def test_ensure_utc_treats_naive_datetime_as_utc() -> None:
    naive = datetime(2026, 7, 11, 15, 18, 9)
    aware = ensure_utc(naive)

    assert aware.tzinfo is not None
    assert ensure_utc(aware) == aware
    assert naive.replace(tzinfo=aware.tzinfo) == aware


def test_naive_expiry_can_be_compared_with_utc_now() -> None:
    future = datetime(2099, 1, 1, 0, 0, 0)
    past = datetime(2000, 1, 1, 0, 0, 0)

    assert ensure_utc(future) > utc_now()
    assert ensure_utc(past) < utc_now()
