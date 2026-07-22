"""Entity extraction using spaCy."""
import spacy
from typing import Dict, Any, List

# Load small English model; for multilingual need multiple models.
_nlp = spacy.load("en_core_web_sm")


def add_entities(record: Dict[str, Any]) -> Dict[str, Any]:
    """Extract named entities and add them to the record."""
    text = record.get("text", "")
    if not text:
        return record
    doc = _nlp(text)
    entities = [{"text": ent.text, "label": ent.label_} for ent in doc.ents]
    record["entities"] = entities
    return record
