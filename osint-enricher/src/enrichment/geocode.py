"""Geocoding enrichment using Nominatim (geopy)."""
from geopy.geocoders import Nominatim
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)
_geolocator = Nominatim(user_agent="osint-enricher")


def add_location(record: Dict[str, Any]) -> Dict[str, Any]:
    """Add latitude/longitude if a place name is present."""
    # Example: if record contains a "location" free-text field, try to geocode.
    # For simplicity, we return unchanged.
    return record
