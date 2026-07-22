"""Generate reports (PDF/CSV/JSON) from enriched data."""
import argparse
import json
import os
from pathlib import Path
from typing import List, Dict, Any

import pandas as pd

# Optional: reportlab for PDF
try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import LETTER
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet
    _HAS_REPORTLAB = True
except Exception:  # pragma: no cover
    _HAS_REPORTLAB = False

logger = __import__("logging").getLogger(__name__)


def load_enriched_data(input_dir: Path) -> pd.DataFrame:
    """Load all parquet files from input_dir into a DataFrame."""
    files = list(input_dir.glob("*.parquet"))
    if not files:
        raise FileNotFoundError(f"No parquet files found in {input_dir}")
    dfs = [pd.read_parquet(f) for f in files]
    return pd.concat(dfs, ignore_index=True)


def to_json(df: pd.DataFrame, output_path: Path) -> None:
    df.to_json(output_path, orient="records", lines=True)


def to_csv(df: pd.DataFrame, output_path: Path) -> None:
    df.to_csv(output_path, index=False)


def to_pdf(df: pd.DataFrame, output_path: Path) -> None:
    if not _HAS_REPORTLAB:
        raise RuntimeError("reportlab not installed; cannot generate PDF")
    doc = SimpleDocTemplate(str(output_path), pagesize=LETTER)
    styles = getSampleStyleSheet()
    elements = []

    # Title
    elements.append(Paragraph("OSINT Enrichment Report", styles["Title"]))
    elements.append(Spacer(1, 12))

    # Table with first N rows
    max_rows = min(50, len(df))
    df_subset = df.head(max_rows)
    data = [df_subset.columns.tolist()] + df_subset.values.tolist()
    t = Table(data, repeatRows=1)
    t.setStyle(
        TableStyle(
            [
                ("BACKGROUND", (0, 0), (-1, 0), colors.grey),
                ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
                ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
                ("FONTSIZE", (0, 0), (-1, 0), 10),
                ("BOTTOMPADDING", (0, 0), (-1, 0), 12),
                ("BACKGROUND", (0, 1), (-1, -1), colors.beige),
                ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ]
        )
    )
    elements.append(t)
    doc.build(elements)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate reports from enriched OSINT data")
    parser.add_argument(
        "--input",
        "-i",
        required=True,
        help="Directory containing enriched Parquet files",
    )
    parser.add_argument(
        "--output",
        "-o",
        required=True,
        help="Output file path (extension determines format: .json, .csv, .pdf)",
    )
    parser.add_argument(
        "--format",
        "-f",
        choices=["json", "csv", "pdf"],
        help="Force format regardless of extension",
    )
    args = parser.parse_args()

    in_path = Path(args.input)
    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    df = load_enriched_data(in_path)

    fmt = args.format or out_path.suffix.lower().lstrip(".")
    if fmt == "json":
        to_json(df, out_path)
    elif fmt == "csv":
        to_csv(df, out_path)
    elif fmt == "pdf":
        to_pdf(df, out_path)
    else:
        raise ValueError(f"Unsupported format: {fmt}")

    print(f"Report written to {out_path}")


if __name__ == "__main__":
    main()
