"""Small normalization helpers used by the offline ranker."""

from __future__ import annotations

import re
from datetime import date, datetime
from typing import Any


WORD_RE = re.compile(r"[a-z0-9+#.]+")


def text(value: Any) -> str:
    """Return a safe, lowercase text representation."""

    if value is None:
        return ""
    return str(value).lower()


def tokens(value: Any) -> set[str]:
    return set(WORD_RE.findall(text(value)))


def has_any(haystack: str, needles: set[str]) -> bool:
    haystack = text(haystack)
    return any(needle in haystack for needle in needles)


def count_any(haystack: str, needles: set[str]) -> int:
    haystack = text(haystack)
    return sum(1 for needle in needles if needle in haystack)


def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))


def safe_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None:
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def parse_date(value: Any) -> date | None:
    if not value:
        return None
    if isinstance(value, date):
        return value
    try:
        return datetime.strptime(str(value)[:10], "%Y-%m-%d").date()
    except ValueError:
        return None


def days_since(value: Any, *, today: date = date(2026, 7, 2)) -> int | None:
    parsed = parse_date(value)
    if parsed is None:
        return None
    return (today - parsed).days
