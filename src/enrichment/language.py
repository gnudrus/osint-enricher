"""Language detection enrichment."""

from __future__ import annotations

from typing import Any, Dict

from langdetect import DetectorFactory, LangDetectException, detect

DetectorFactory.seed = 0


def add_language(record: Dict[str, Any]) -> Dict[str, Any]:
    text = str(record.get("text") or "").strip()
    if not text or record.get("language"):
        return record
    try:
        record["language"] = detect(text)
    except LangDetectException:
        record["language"] = "unknown"
    return record
