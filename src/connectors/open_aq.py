"""OpenAQ locations connector."""

from __future__ import annotations

import os
from typing import Any, Dict, Iterable

import requests

from .base import BaseConnector


class OpenAQConnector(BaseConnector):
    def __init__(self, api_key: str | None = None, *, session: Any = requests):
        self.api_key = api_key or os.getenv("OPENAQ_API_KEY")
        self.base_url = "https://api.openaq.org/v3"
        self.session = session

    def fetch(self, since: str) -> Iterable[Dict[str, Any]]:
        headers = {"X-API-Key": self.api_key} if self.api_key else {}
        response = self.session.get(
            f"{self.base_url}/locations",
            params={"limit": 100},
            headers=headers,
            timeout=20,
        )
        response.raise_for_status()
        for location in response.json().get("results", []):
            coordinates = location.get("coordinates") or {}
            yield {
                "id": str(location.get("id")),
                "source": "openaq",
                "text": location.get("name") or "Air-quality monitoring location",
                "timestamp": location.get("datetimeLast", {}).get("utc"),
                "country": (location.get("country") or {}).get("code"),
                "latitude": coordinates.get("latitude"),
                "longitude": coordinates.get("longitude"),
                "sensors": location.get("sensors", []),
            }
