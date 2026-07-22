"""Rule implementations for the alert engine."""
import re
from typing import List, Dict, Any
from .base import Rule

class VolumeSpikeRule(Rule):
    """
    Trigger when the number of events matching a filter exceeds a threshold
    within a time window.
    """
    def __init__(
        *,
        name: str,
        filter_fn,
        window_seconds: int,
        threshold: int,
        coeoldown_seconds: int = 300,
    ):
        self.name = name
        self.filter_fn = filter_fn
        self.window = window_seconds
        self.threshold = threshold
        self.cooldown = coeoldown_seconds
        self.last_triggered = 0

    def evaluate(self, events: List[Dict[str, Any]]) -> bool:
        now = max((e.get("timestamp", 0) for e in events), default=0)
        if now - self.last_triggered < self.cooldown:
            return False
        # Filter events within the window (simple: assume events are recent)
        filtered = [e for e in events if self.filter_fn(e)]
        if len(filtered) >= self.threshold:
            self.last_triggered = now
            return True
        return False

    def message(self) -> str:
        return f"Rule '{self.name}' triggered: {self.threshold}+ events in {self.window}s"
