"""Entry point for running the enrichment pipeline."""
import argparse
import logging
import os
from pathlib import Path

import pandas as pd  # assuming we store as Parquet; adjust as needed

from .geocode import add_location
from .sentiment import add_sentiment
from .entity import add_entities
from .source_score import add_source_score

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger(__name__)


def enrich_record(record: dict) -> dict:
    """Apply all enrichment steps to a single record."""
    for func in (add_location, add_sentiment, add_entities, add_source_score):
        try:
            record = func(record)
        except Exception as exc:  # pragma: no cover - defensive
            logger.warning("Enrichment step %s failed: %s", func.__name__, exc)
    return record


def run(input_dir: str, output_dir: str) -> None:
    """Read raw JSON/JSONL files, enrich, and write Parquet."""
    in_path = Path(input_dir)
    out_path = Path(output_dir)
    out_path.mkdir(parents=True, exist_ok=True)

    # For demo, we assume each file is a JSON lines file.
    for file in in_path.glob("*.json*"):
        logger.info("Processing %s", file.name)
        # Read lines
        records = []
        with open(file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    # Expect JSON per line
                    import json
                    rec = json.loads(line)
                    records.append(rec)
                except json.JSONDecodeError:
                    # If file is a single JSON array, fallback
                    pass
        if not records:
            # Try to read whole file as JSON
            import json
            with open(file, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list):
                    records = data
                else:
                    records = [data]

        enriched = [enrich_record(r) for r in records]
        # Write as Parquet (requires pyarrow or fastparquet)
        df = pd.DataFrame(enriched)
        out_file = out_path / f"{file.stem}.parquet"
        df.to_parquet(out_file, index=False)
        logger.info("Written %d records to %s", len(enriched), out_file)


def main() -> None:
    parser = argparse.ArgumentParser(description="Enrich raw OSINT data")
    parser.add_argument(
        "--input",
        "-i",
        required=True,
        help="Directory containing raw JSON/JSONL files",
    )
    parser.add_argument(
        "--output",
        "-o",
        required=True,
        help="Directory to write enriched Parquet files",
    )
    args = parser.parse_args()
    run(args.input, args.output)


if __name__ == "__main__":
    main()
