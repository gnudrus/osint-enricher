"""OpenAQ connector for air quality data."""
import requests
from typing import Iterable, Dict, Any
from .base import BaseConnector


class OpenAQConnector(BaseConnector):
    def __init__(self, api_key: str | None = None):
        self.api_key = api_key
        self.base_url = "https://api.openaq.org/v2"

    def fetch(self, since: str) -> Iterable[Dict[str, Any]]:
        # Stub
        yield {}
