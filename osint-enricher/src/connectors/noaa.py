"""NOAA alerts connector."""
import requests
from typing import Iterable, Dict, Any
from .base import BaseConnector


class NOAAConnector(BaseConnector):
    def __init__(self):
        self.base_url = "https://api.weather.gov/alerts"

    def fetch(self, since: str) -> Iterable[Dict[str, Any]]:
        # Stub
        yield {}
