"""Rule implementations for the alert engine."""

from __future__ import annotations

import time
from datetime import datetime
from typing import Any, Callable, Dict, List

from .base import Rule


def _timestamp(value: Any) -> float | None:
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str) and value:
        try:
            return datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp()
        except ValueError:
            return None
    return None


class VolumeSpikeRule(Rule):
    """Trigger when matching events meet a threshold inside a time window."""

    def __init__(
        self,
        *,
        name: str,
        filter_fn: Callable[[Dict[str, Any]], bool],
        window_seconds: int,
        threshold: int,
        cooldown_seconds: int = 300,
    ):
        if window_seconds <= 0 or threshold <= 0 or cooldown_seconds < 0:
            raise ValueError("window and threshold must be positive; cooldown cannot be negative")
        self.name = name
        self.filter_fn = filter_fn
        self.window = window_seconds
        self.threshold = threshold
        self.cooldown = cooldown_seconds
        self.last_triggered: float | None = None

    def evaluate(self, events: List[Dict[str, Any]]) -> bool:
        timestamps = [stamp for event in events if (stamp := _timestamp(event.get("timestamp"))) is not None]
        now = max(timestamps, default=time.time())
        if self.last_triggered is not None and now - self.last_triggered < self.cooldown:
            return False

        matching = []
        for event in events:
            stamp = _timestamp(event.get("timestamp"))
            inside_window = stamp is None or now - self.window <= stamp <= now
            if inside_window and self.filter_fn(event):
                matching.append(event)
        if len(matching) < self.threshold:
            return False
        self.last_triggered = now
        return True

    def message(self) -> str:
        return f"Rule '{self.name}' triggered: {self.threshold}+ events in {self.window}s"
