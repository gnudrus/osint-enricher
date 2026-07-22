"""Sentiment enrichment with an optional transformer backend."""

from __future__ import annotations

import logging
import re
from functools import lru_cache
from typing import Any, Callable, Dict

logger = logging.getLogger(__name__)
_MODEL_NAME = "distilbert-base-uncased-finetuned-sst-2-english"
_POSITIVE = {"good", "great", "safe", "success", "positive", "improved", "love", "excellent"}
_NEGATIVE = {"bad", "danger", "failure", "negative", "worse", "hate", "critical", "emergency"}


@lru_cache(maxsize=1)
def _load_pipeline() -> Callable[[str], list[dict[str, Any]]] | None:
    try:
        import torch
        from transformers import pipeline

        return pipeline(
            "sentiment-analysis",
            model=_MODEL_NAME,
            device=0 if torch.cuda.is_available() else -1,
        )
    except (ImportError, OSError) as exc:
        logger.info("Transformer sentiment backend unavailable; using lexical fallback: %s", exc)
        return None


def _fallback_sentiment(text: str) -> tuple[str, float]:
    words = set(re.findall(r"[a-z]+", text.lower()))
    balance = len(words & _POSITIVE) - len(words & _NEGATIVE)
    if balance > 0:
        return "POSITIVE", min(0.99, 0.55 + 0.1 * balance)
    if balance < 0:
        return "NEGATIVE", min(0.99, 0.55 + 0.1 * abs(balance))
    return "NEUTRAL", 0.5


def add_sentiment(record: Dict[str, Any]) -> Dict[str, Any]:
    text = str(record.get("text") or "").strip()
    if not text:
        return record
    sentiment_pipeline = _load_pipeline()
    if sentiment_pipeline is None:
        label, score = _fallback_sentiment(text)
    else:
        result = sentiment_pipeline(text[:512])[0]
        label, score = str(result["label"]), float(result["score"])
    record["sentiment_label"] = label
    record["sentiment_score"] = score
    return record
