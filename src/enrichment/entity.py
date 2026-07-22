"""Entity extraction with optional spaCy support."""

from __future__ import annotations

import logging
import re
from functools import lru_cache
from typing import Any, Dict

logger = logging.getLogger(__name__)


@lru_cache(maxsize=1)
def _load_nlp():
    try:
        import spacy

        return spacy.load("en_core_web_sm")
    except (ImportError, OSError) as exc:
        logger.info("spaCy entity model unavailable; using pattern fallback: %s", exc)
        return None


def add_entities(record: Dict[str, Any]) -> Dict[str, Any]:
    text = str(record.get("text") or "").strip()
    if not text:
        return record
    nlp = _load_nlp()
    if nlp is not None:
        record["entities"] = [
            {"text": entity.text, "label": entity.label_} for entity in nlp(text).ents
        ]
        return record

    matches = re.findall(r"\b[A-Z][A-Za-z0-9_-]*(?:\s+[A-Z][A-Za-z0-9_-]*){0,2}\b", text)
    record["entities"] = [
        {"text": value, "label": "PROPER_NOUN"} for value in dict.fromkeys(matches)
    ]
    return record
