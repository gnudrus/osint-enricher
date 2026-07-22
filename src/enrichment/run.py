"""Command-line entry point for the enrichment pipeline."""

from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path
from typing import Any

import pandas as pd

from .base import enrich_record

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def read_records(path: Path) -> list[dict[str, Any]]:
    text = path.read_text(encoding="utf-8").strip()
    if not text:
        return []
    try:
        value = json.loads(text)
    except json.JSONDecodeError:
        records = []
        for line_number, line in enumerate(text.splitlines(), start=1):
            if not line.strip():
                continue
            try:
                value = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSON in {path} at line {line_number}") from exc
            if not isinstance(value, dict):
                raise ValueError(f"JSONL record at line {line_number} must be an object")
            records.append(value)
        return records
    if isinstance(value, dict):
        return [value]
    if isinstance(value, list) and all(isinstance(item, dict) for item in value):
        return value
    raise ValueError(f"{path} must contain a JSON object, an array of objects, or JSONL")


def run(input_dir: str | Path, output_dir: str | Path) -> list[Path]:
    source_dir = Path(input_dir)
    if not source_dir.is_dir():
        raise NotADirectoryError(f"Input directory not found: {source_dir}")
    destination_dir = Path(output_dir)
    destination_dir.mkdir(parents=True, exist_ok=True)

    outputs = []
    for source_file in sorted(source_dir.glob("*.json*")):
        records = read_records(source_file)
        enriched = [enrich_record(record) for record in records]
        output_file = destination_dir / f"{source_file.stem}.parquet"
        pd.DataFrame(enriched).to_parquet(output_file, index=False)
        outputs.append(output_file)
        logger.info("Wrote %d records to %s", len(enriched), output_file)
    return outputs


def main() -> None:
    parser = argparse.ArgumentParser(description="Enrich raw OSINT JSON/JSONL data")
    parser.add_argument("--input", "-i", required=True, help="Input directory")
    parser.add_argument("--output", "-o", required=True, help="Output directory")
    args = parser.parse_args()
    run(args.input, args.output)


if __name__ == "__main__":
    main()
