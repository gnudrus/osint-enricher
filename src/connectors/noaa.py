"""NOAA/NWS active-alert connector."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Iterable

import requests

from .base import BaseConnector
from .utils import since_to_datetime


class NOAAConnector(BaseConnector):
    def __init__(self, *, session: Any = requests):
        self.base_url = "https://api.weather.gov/alerts/active"
        self.session = session

    def fetch(self, since: str) -> Iterable[Dict[str, Any]]:
        cutoff = since_to_datetime(since)
        response = self.session.get(
            self.base_url,
            headers={"Accept": "application/geo+json", "User-Agent": "osint-enricher/0.2"},
            timeout=20,
        )
        response.raise_for_status()
        for feature in response.json().get("features", []):
            props = feature.get("properties", {})
            sent_raw = props.get("sent")
            sent = datetime.fromisoformat(sent_raw.replace("Z", "+00:00")) if sent_raw else None
            if sent and sent < cutoff:
                continue
            yield {
                "id": feature.get("id"),
                "source": "noaa",
                "text": props.get("description") or props.get("headline") or "",
                "title": props.get("event"),
                "timestamp": sent.isoformat() if sent else None,
                "severity": props.get("severity"),
                "area": props.get("areaDesc"),
                "geometry": feature.get("geometry"),
            }
