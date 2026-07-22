"""Geocoding enrichment using Nominatim."""

from __future__ import annotations

import logging
from functools import lru_cache
from typing import Any, Dict

from geopy.exc import GeocoderServiceError, GeocoderTimedOut
from geopy.geocoders import Nominatim

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def _geolocator() -> Nominatim:
    return Nominatim(user_agent="osint-enricher/0.2")


def add_location(record: Dict[str, Any]) -> Dict[str, Any]:
    if record.get("latitude") is not None and record.get("longitude") is not None:
        return record
    place = str(record.get("location") or "").strip()
    if not place:
        return record
    try:
        result = _geolocator().geocode(place, exactly_one=True, timeout=10)
    except (GeocoderServiceError, GeocoderTimedOut) as exc:
        logger.warning("Geocoding failed for %s: %s", place, exc)
        return record
    if result:
        record["latitude"] = float(result.latitude)
        record["longitude"] = float(result.longitude)
    return record
