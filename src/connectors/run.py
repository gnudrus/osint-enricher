"""Command-line entry point for data ingestion."""

from __future__ import annotations

import argparse
import json
import logging
import os
from pathlib import Path
from typing import Any

from .noaa import NOAAConnector
from .open_aq import OpenAQConnector
from .reddit import RedditConnector
from .rss import RSSConnector
from .twitter import TwitterConnector

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def get_connector(name: str) -> Any:
    normalized = name.lower().replace("-", "_")
    if normalized == "twitter":
        return TwitterConnector()
    if normalized == "reddit":
        return RedditConnector()
    if normalized == "rss":
        urls = [url.strip() for url in os.getenv("RSS_FEEDS", "").split(",") if url.strip()]
        if not urls:
            urls = ["https://feeds.bbci.co.uk/news/world/rss.xml"]
        return RSSConnector(urls)
    if normalized in {"openaq", "open_aq"}:
        return OpenAQConnector()
    if normalized == "noaa":
        return NOAAConnector()
    raise ValueError(f"Unknown connector: {name}")


def _source_names(values: list[str]) -> list[str]:
    return [name.strip() for value in values for name in value.split(",") if name.strip()]


def ingest(sources: list[str], since: str, output: Path) -> int:
    output.mkdir(parents=True, exist_ok=True)
    failures = 0
    for source in _source_names(sources):
        try:
            connector = get_connector(source)
            records = list(connector.fetch(since))
            destination = output / f"{source}.jsonl"
            with destination.open("w", encoding="utf-8") as handle:
                for record in records:
                    handle.write(json.dumps(record, ensure_ascii=False) + "\n")
            logger.info("Saved %d %s records to %s", len(records), source, destination)
        except Exception as exc:
            failures += 1
            logger.error("Failed to fetch from %s: %s", source, exc)
    return failures


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest public OSINT data")
    parser.add_argument("--sources", "-s", nargs="+", required=True, help="Sources, separated by spaces or commas")
    parser.add_argument("--since", default="30m", help="Relative duration (30m, 2h, 1d) or ISO-8601 time")
    parser.add_argument("--output", "-o", type=Path, required=True, help="Output directory for JSONL files")
    args = parser.parse_args()
    if ingest(args.sources, args.since, args.output):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
