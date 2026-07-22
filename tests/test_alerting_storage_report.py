import json

import pandas as pd
import pytest

from src.alerting.rules import VolumeSpikeRule
from src.alerting.run import evaluate, load_events, load_rules
from src.report.run import load_enriched_data, to_csv, to_json, to_pdf
from src.storage.local_store import LocalStore


def test_volume_spike_window_and_cooldown():
    rule = VolumeSpikeRule(
        name="surge", filter_fn=lambda event: event["source"] == "rss",
        window_seconds=60, threshold=2, cooldown_seconds=30,
    )
    events = [
        {"source": "rss", "timestamp": 1000},
        {"source": "rss", "timestamp": 1010},
        {"source": "rss", "timestamp": 900},
    ]
    assert rule.evaluate(events) is True
    assert rule.evaluate(events) is False
    assert "surge" in rule.message()


def test_volume_spike_validates_configuration():
    with pytest.raises(ValueError):
        VolumeSpikeRule(name="bad", filter_fn=lambda event: True, window_seconds=0, threshold=1)


def test_rule_config_and_event_evaluation(tmp_path):
    config = tmp_path / "rules.yaml"
    config.write_text(
        "rules:\n"
        "  - name: alert\n"
        "    type: volume_spike\n"
        "    source: rss\n"
        "    keyword: storm\n"
        "    window_seconds: 300\n"
        "    threshold: 2\n"
    )
    events = tmp_path / "events.jsonl"
    events.write_text(
        json.dumps({"source": "rss", "text": "storm warning", "timestamp": 1000}) + "\n" +
        json.dumps({"source": "rss", "text": "storm update", "timestamp": 1010}) + "\n"
    )
    assert len(load_rules(config)) == 1
    assert len(load_events(events)) == 2
    assert evaluate(config, events) == ["Rule 'alert' triggered: 2+ events in 300s"]


def test_load_events_rejects_non_objects(tmp_path):
    path = tmp_path / "bad.jsonl"
    path.write_text("[]\n")
    with pytest.raises(ValueError, match="must be an object"):
        load_events(path)


def test_local_store_round_trip_listing_delete_and_traversal(tmp_path):
    store = LocalStore(tmp_path / "storage")
    store.put_object("events", "2026/item.json", b"payload")
    assert store.get_object("events", "2026/item.json") == b"payload"
    assert list(store.list_objects("events", "2026")) == ["2026/item.json"]
    store.delete_object("events", "2026/item.json")
    assert list(store.list_objects("events")) == []
    with pytest.raises(ValueError):
        store.put_object("events", "../../escape", b"bad")


def test_report_outputs(tmp_path):
    frame = pd.DataFrame([{"id": "1", "text": "event"}])
    parquet = tmp_path / "input"
    parquet.mkdir()
    frame.to_parquet(parquet / "events.parquet", index=False)
    loaded = load_enriched_data(parquet)
    assert loaded.to_dict("records") == [{"id": "1", "text": "event"}]

    json_path = tmp_path / "report.json"
    csv_path = tmp_path / "report.csv"
    pdf_path = tmp_path / "report.pdf"
    to_json(loaded, json_path)
    to_csv(loaded, csv_path)
    to_pdf(loaded, pdf_path)
    assert '"text":"event"' in json_path.read_text()
    assert "text" in csv_path.read_text()
    assert pdf_path.read_bytes().startswith(b"%PDF")


def test_report_requires_parquet_files(tmp_path):
    with pytest.raises(FileNotFoundError):
        load_enriched_data(tmp_path)
