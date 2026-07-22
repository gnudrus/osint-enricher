"""Sentiment analysis using a lightweight DistilBERT model."""
from transformers import AutoModelForSequenceClassification, AutoTokenizer, pipeline
from typing import Dict, Any
import torch

# Load model once (singleton)
_MODEL_NAME = "distilbert-base-uncased-finetuned-sst-2-english"
_tokenizer = AutoTokenizer.from_pretrained(_MODEL_NAME)
_model = AutoModelForSequenceClassification.from_pretrained(_MODEL_NAME)
_sentiment_pipe = pipeline(
    "sentiment analysis",
    model=_model,
    tokenizer=_tokenizer,
    return_all_scores=False,
    device=0 if torch.cuda.is_available() else -1,
)


def add_sentiment(record: Dict[str, Any]) -> Dict[str, Any]:
    """Add sentiment label and score to the record."""
    text = record.get("text", "")
    if not text:
        return record
    result = _sentiment_pipe(text[:512])  # truncate to model max length
    # result is list of dicts with 'label' and 'score'
    label = result[0]["label"]
    score = float(result[0]["score"])
    record["sentiment_label"] = label
    record["sentiment_score"] = score
    return record
