"""Source credibility scoring."""
from typing import Dict, Any

def add_source_score(record: Dict[str, Any]) -> Dict[str, Any]:
    """Compute a simple credibility score based on source domain."""
    source = record.get("source", "").lower()
    # Example scoring: known reputable domains get higher score.
    trusted = {"bbc.com", "reuters.com", "ap.org", "nytimes.com", "theguardian.com"}
    score = 1.0 if any(domain in source for domain in trusted) else 0.5
    record["source_score"] = score
    return record
