"""Shared helpers for connector time filters."""

from __future__ import annotations

import re
from datetime import datetime, timedelta, timezone

_RELATIVE_TIME = re.compile(r"^(?P<amount>\d+)(?P<unit>[mhd])$")


def since_to_datetime(value: str, *, now: datetime | None = None) -> datetime:
    """Convert a relative duration or ISO-8601 timestamp to an aware UTC datetime."""
    current = now or datetime.now(timezone.utc)
    match = _RELATIVE_TIME.fullmatch(value.strip().lower())
    if match:
        amount = int(match.group("amount"))
        unit = match.group("unit")
        delta = {
            "m": timedelta(minutes=amount),
            "h": timedelta(hours=amount),
            "d": timedelta(days=amount),
        }[unit]
        return current - delta

    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)
