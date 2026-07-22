from datetime import datetime, timedelta, timezone
from types import SimpleNamespace

import pytest

from src.connectors.noaa import NOAAConnector
from src.connectors.open_aq import OpenAQConnector
from src.connectors.reddit import RedditConnector
from src.connectors.rss import RSSConnector
from src.connectors.run import _source_names, ingest
from src.connectors.twitter import TwitterConnector
from src.connectors.utils import since_to_datetime


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def raise_for_status(self):
        return None

    def json(self):
        return self.payload


class FakeSession:
    def __init__(self, payload):
        self.payload = payload
        self.calls = []

    def get(self, *args, **kwargs):
        self.calls.append((args, kwargs))
        return FakeResponse(self.payload)


def test_since_to_datetime_supports_relative_and_iso_values():
    now = datetime(2026, 1, 2, 12, tzinfo=timezone.utc)
    assert since_to_datetime("30m", now=now) == now - timedelta(minutes=30)
    assert since_to_datetime("2h", now=now) == now - timedelta(hours=2)
    assert since_to_datetime("1d", now=now) == now - timedelta(days=1)
    assert since_to_datetime("2026-01-01T10:00:00Z").tzinfo == timezone.utc


def test_since_to_datetime_rejects_invalid_value():
    with pytest.raises(ValueError):
        since_to_datetime("yesterday")


def test_twitter_connector_maps_tweets():
    created = datetime.now(timezone.utc)
    tweet = SimpleNamespace(id=7, text="Breaking update", created_at=created, lang="en", author_id=9)
    client = SimpleNamespace(
        search_recent_tweets=lambda **kwargs: SimpleNamespace(data=[tweet])
    )
    records = list(TwitterConnector(client=client, query="osint").fetch("30m"))
    assert records[0]["id"] == "7"
    assert records[0]["source"] == "twitter"
    assert records[0]["language"] == "en"


def test_reddit_connector_filters_old_submissions():
    now = datetime.now(timezone.utc).timestamp()
    fresh = SimpleNamespace(
        id="a", title="Title", selftext="Body", created_utc=now,
        url="https://reddit.test/a", subreddit="osint", score=4,
    )
    old = SimpleNamespace(
        id="b", title="Old", selftext="", created_utc=now - 7200,
        url="https://reddit.test/b", subreddit="osint", score=1,
    )
    listing = SimpleNamespace(new=lambda limit: [fresh, old])
    client = SimpleNamespace(subreddit=lambda name: listing)
    records = list(RedditConnector(client=client, subreddit="osint").fetch("1h"))
    assert [record["id"] for record in records] == ["a"]
    assert records[0]["text"] == "Title\n\nBody"


def test_rss_connector_maps_feed_entries(monkeypatch):
    published = datetime.now(timezone.utc).timetuple()
    parsed = SimpleNamespace(
        bozo=False,
        entries=[{
            "id": "item-1", "title": "Headline", "summary": "Summary",
            "link": "https://example.test/item", "published_parsed": published,
        }],
    )
    monkeypatch.setattr("src.connectors.rss.feedparser.parse", lambda url: parsed)
    record = list(RSSConnector(["https://example.test/feed"]).fetch("1d"))[0]
    assert record["source"] == "rss"
    assert record["text"] == "Summary"


def test_noaa_connector_filters_and_maps_alerts():
    sent = datetime.now(timezone.utc).isoformat()
    session = FakeSession({"features": [{
        "id": "alert-1", "geometry": None,
        "properties": {"sent": sent, "event": "Storm", "headline": "Warning", "severity": "Severe"},
    }]})
    record = list(NOAAConnector(session=session).fetch("1d"))[0]
    assert record["id"] == "alert-1"
    assert record["title"] == "Storm"
    assert session.calls[0][1]["timeout"] == 20


def test_openaq_connector_maps_locations():
    session = FakeSession({"results": [{
        "id": 42, "name": "Central", "country": {"code": "IT"},
        "coordinates": {"latitude": 41.9, "longitude": 12.5},
        "datetimeLast": {"utc": "2026-01-01T00:00:00Z"}, "sensors": [],
    }]})
    record = list(OpenAQConnector(api_key="key", session=session).fetch("1h"))[0]
    assert record["source"] == "openaq"
    assert record["country"] == "IT"
    assert session.calls[0][1]["headers"] == {"X-API-Key": "key"}


def test_ingest_splits_sources_and_writes_jsonl(tmp_path, monkeypatch):
    connector = SimpleNamespace(fetch=lambda since: [{"id": "1", "text": "ok"}])
    monkeypatch.setattr("src.connectors.run.get_connector", lambda name: connector)
    assert _source_names(["rss,noaa", "openaq"]) == ["rss", "noaa", "openaq"]
    assert ingest(["rss,noaa"], "30m", tmp_path) == 0
    assert '"text": "ok"' in (tmp_path / "rss.jsonl").read_text()
    assert (tmp_path / "noaa.jsonl").exists()
