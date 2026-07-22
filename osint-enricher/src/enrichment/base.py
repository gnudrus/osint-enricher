"""Base enrichment transformations."""
from __future__ import annotations
from typing import Dict, Any


def enrich_record(record: Dict[str, Any]) -> Dict[str, Any]:
    """
    Apply all enrichment steps to a raw record.
    This is a pipeline that calls individual enrichment functions.
    """
    # Placeholder: implement actual enrichment steps
    return record
