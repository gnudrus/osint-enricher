import json
from types import SimpleNamespace

import pandas as pd
import pytest

from src.enrichment.base import enrich_record
from src.enrichment.entity import add_entities
from src.enrichment.geocode import add_location
from src.enrichment.language import add_language
from src.enrichment.run import read_records, run
from src.enrichment.sentiment import add_sentiment
from src.enrichment.source_score import add_source_score


def test_language_detection_and_empty_text():
    assert add_language({"text": "This is a simple English sentence."})["language"] == "en"
    assert add_language({"text": ""}) == {"text": ""}


@pytest.mark.parametrize(
    ("text", "label"),
    [("great success", "POSITIVE"), ("critical failure", "NEGATIVE"), ("plain update", "NEUTRAL")],
)
def test_sentiment_fallback(monkeypatch, text, label):
    monkeypatch.setattr("src.enrichment.sentiment._load_pipeline", lambda: None)
    assert add_sentiment({"text": text})["sentiment_label"] == label


def test_entity_fallback_deduplicates_matches(monkeypatch):
    monkeypatch.setattr("src.enrichment.entity._load_nlp", lambda: None)
    result = add_entities({"text": "Alice Smith met Bob in Rome. Alice Smith agreed."})
    names = [entity["text"] for entity in result["entities"]]
    assert names.count("Alice Smith") == 1
    assert "Rome" in names


def test_geocoding_and_existing_coordinates(monkeypatch):
    locator = SimpleNamespace(
        geocode=lambda *args, **kwargs: SimpleNamespace(latitude=41.9028, longitude=12.4964)
    )
    monkeypatch.setattr("src.enrichment.geocode._geolocator", lambda: locator)
    result = add_location({"location": "Rome"})
    assert result["latitude"] == 41.9028
    existing = {"location": "Rome", "latitude": 1.0, "longitude": 2.0}
    assert add_location(existing) == existing


def test_source_score_uses_domain_boundaries():
    assert add_source_score({"url": "https://www.reuters.com/world"})["source_score"] == 1.0
    assert add_source_score({"url": "https://evilreuters.com"})["source_score"] == 0.5


def test_enrich_record_preserves_input_and_adds_fields(monkeypatch):
    monkeypatch.setattr("src.enrichment.sentiment._load_pipeline", lambda: None)
    monkeypatch.setattr("src.enrichment.entity._load_nlp", lambda: None)
    source = {"text": "Great update from Rome", "url": "https://bbc.com/news"}
    result = enrich_record(source)
    assert result is not source
    assert result["sentiment_label"] == "POSITIVE"
    assert result["source_score"] == 1.0


def test_read_records_supports_object_array_and_jsonl(tmp_path):
    object_file = tmp_path / "object.json"
    object_file.write_text('{"id": 1}')
    assert read_records(object_file) == [{"id": 1}]

    array_file = tmp_path / "array.json"
    array_file.write_text('[{"id": 1}, {"id": 2}]')
    assert len(read_records(array_file)) == 2

    lines_file = tmp_path / "lines.jsonl"
    lines_file.write_text('{"id": 1}\n{"id": 2}\n')
    assert len(read_records(lines_file)) == 2


def test_read_records_reports_invalid_line(tmp_path):
    path = tmp_path / "bad.jsonl"
    path.write_text('{"id": 1}\nnot-json\n')
    with pytest.raises(ValueError, match="line 2"):
        read_records(path)


def test_enrichment_run_writes_parquet(tmp_path, monkeypatch):
    source = tmp_path / "raw"
    destination = tmp_path / "enriched"
    source.mkdir()
    (source / "events.jsonl").write_text(json.dumps({"id": "1", "text": "update"}) + "\n")
    monkeypatch.setattr("src.enrichment.run.enrich_record", lambda record: {**record, "done": True})
    outputs = run(source, destination)
    assert len(outputs) == 1
    frame = pd.read_parquet(outputs[0])
    assert frame.loc[0, "done"]
