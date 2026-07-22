"""Simple, transparent source-domain scoring."""

from __future__ import annotations

from typing import Any, Dict
from urllib.parse import urlparse

_TRUSTED_DOMAINS = {"ap.org", "bbc.com", "reuters.com", "nytimes.com", "theguardian.com"}


def add_source_score(record: Dict[str, Any]) -> Dict[str, Any]:
    raw_source = str(record.get("source_url") or record.get("url") or record.get("source") or "")
    parsed = urlparse(raw_source if "://" in raw_source else f"//{raw_source}")
    hostname = (parsed.hostname or "").lower().removeprefix("www.")
    trusted = any(hostname == domain or hostname.endswith(f".{domain}") for domain in _TRUSTED_DOMAINS)
    record["source_score"] = 1.0 if trusted else 0.5
    return record
