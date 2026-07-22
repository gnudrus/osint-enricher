"""Base classes for connectors."""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Iterable, Dict, Any


class BaseConnector(ABC):
    """Abstract connector to fetch raw data from a source."""

    @abstractmethod
    def fetch(self, since: str) -> Iterable[Dict[str, Any]]:
        """
        Yield raw event dictionaries.

        Args:
            since: ISO8601 timestamp or relative string (e.g., "30m").

        Returns:
            An iterable of raw events.
        """
        raise NotImplementedError
