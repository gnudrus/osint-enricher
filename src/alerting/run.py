"""Command-line entry point for alert rules."""

from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path
from typing import Any

import yaml

from .rules import VolumeSpikeRule

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def _event_filter(source: str | None, keyword: str | None):
    def matches(event: dict[str, Any]) -> bool:
        source_matches = not source or str(event.get("source", "")).lower() == source.lower()
        keyword_matches = not keyword or keyword.lower() in str(event.get("text", "")).lower()
        return source_matches and keyword_matches

    return matches


def load_rules(config_path: Path) -> list[VolumeSpikeRule]:
    with config_path.open(encoding="utf-8") as handle:
        config = yaml.safe_load(handle) or {}
    if not isinstance(config, dict) or not isinstance(config.get("rules", []), list):
        raise ValueError("Rule configuration must contain a 'rules' list")

    rules = []
    for item in config.get("rules", []):
        if item.get("type") != "volume_spike":
            logger.warning("Unsupported rule type: %s", item.get("type"))
            continue
        rules.append(
            VolumeSpikeRule(
                name=item.get("name", "unnamed"),
                filter_fn=_event_filter(item.get("source"), item.get("keyword")),
                window_seconds=int(item.get("window_seconds", 300)),
                threshold=int(item.get("threshold", 10)),
                cooldown_seconds=int(item.get("cooldown_seconds", item.get("cooldown", 600))),
            )
        )
    return rules


def load_events(input_path: Path) -> list[dict[str, Any]]:
    paths = sorted(input_path.rglob("*.jsonl")) if input_path.is_dir() else [input_path]
    events = []
    for path in paths:
        with path.open(encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, start=1):
                if not line.strip():
                    continue
                try:
                    event = json.loads(line)
                except json.JSONDecodeError as exc:
                    raise ValueError(f"Invalid JSON in {path} at line {line_number}") from exc
                if not isinstance(event, dict):
                    raise ValueError(f"Event in {path} at line {line_number} must be an object")
                events.append(event)
    return events


def evaluate(config_path: Path, input_path: Path) -> list[str]:
    events = load_events(input_path)
    messages = [rule.message() for rule in load_rules(config_path) if rule.evaluate(events)]
    for message in messages:
        logger.info("Trigger: %s", message)
    return messages


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate alert rules against JSONL events")
    parser.add_argument("--config", "-c", type=Path, default=Path("config/rules.yaml"))
    parser.add_argument("--input", "-i", type=Path, required=True)
    args = parser.parse_args()
    evaluate(args.config, args.input)


if __name__ == "__main__":
    main()
