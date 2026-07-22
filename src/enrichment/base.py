"""Reusable enrichment pipeline."""

from __future__ import annotations

import logging
from typing import Any, Dict

from .entity import add_entities
from .geocode import add_location
from .language import add_language
from .sentiment import add_sentiment
from .source_score import add_source_score

logger = logging.getLogger(__name__)

ENRICHMENT_STEPS = (add_language, add_location, add_sentiment, add_entities, add_source_score)


def enrich_record(record: Dict[str, Any]) -> Dict[str, Any]:
    result = dict(record)
    for step in ENRICHMENT_STEPS:
        try:
            result = step(result)
        except Exception as exc:  # defensive isolation between enrichment backends
            logger.warning("Enrichment step %s failed: %s", step.__name__, exc)
    return result
