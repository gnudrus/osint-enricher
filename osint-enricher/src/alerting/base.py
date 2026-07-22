"""Base classes for alerting."""
from abc import ABC, abstractmethod
from typing import Dict, Any

class Notifier(ABC):
    @abstractmethod
    def send(self, message: str, **kwargs) -> None:
        """Send a notification."""
        pass

class Rule(ABC):
    @abstractmethod
    def evaluate(self, events: list[dict]) -> bool:
        """Return True if the rule triggers."""
        pass

    @abstractmethod
    def message(self) -> str:
        """Return a human-readable description of the alert."""
        pass
