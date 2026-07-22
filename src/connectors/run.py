"""Entry point for running data ingestion."""
import argparse
import logging
from pathlib import Path
import json
import os
from typing import List, Dict, Any

from .twitter import TwitterConnector
from .reddit import RedditConnector
from .rss import RSSConnector
from .open_aq import OpenAQConnector
from .noaa import NOAAConnector

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def get_connector(name: str) -> object:
    name = name.lower()
    if name == "twitter":
        return TwitterConnector()
    if name == "reddit":
        return RedditConnector()
    if name == "rss":
        # Example URLs – replace with actual feeds or read from config
        return RSSConnector([
            "http://rss.cnn.com/rss/edition.rss",
            "https://www.bbc.co.uk/news/world/rss/about.xml",
        ])
    if name == "open_aq":
        return OpenAQConnector()
    if name == "noaa":
        return NOAAConnector()
    raise ValueError(f"Unknown connector: {name}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Ingest raw OSINT data from various sources")
    parser.add_argument(
        "--sources",
        "-s",
        nargs="+",
        required=True,
        help="Names of sources to fetch (e.g., twitter reddit rss)",
    )
    parser.add_argument(
        "--since",
        default="30m",
        help="How far back to fetch (e.g., 10m, 2h, 1d). Passed to each connector.",
    )
    parser.add_argument(
        "--output",
        "-o",
        required=True,
        help="Directory to write raw JSON lines files (one per source)",
    )
    args = parser.parse_args()

    out_dir = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)

    for src in args.sources:
        try:
            conn = get_connector(src)
            logger.info("Fetching from %s", src)
            records: List[Dict[str, Any]] = list(conn.fetch(args.since))
            out_file = out_dir / f"{src}.jsonl"
            with out_file.open("w", encoding="utf-8") as f:
                for rec in records:
                    f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            logger.info("Saved %d records to %s", len(records), out_file)
        except Exception as exc:  # pragma: no cover
            logger.error("Failed to fetch from %s: %s", src, exc)


if __name__ == "__main__":
    main()
