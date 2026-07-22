OSINT-Enricher
A lightweight, open-source toolkit for enriching open-source intelligence (OSINT) data. Designed to be run locally (via Docker-Compose) and to showcase data-engineering, NLP, and API integration skills.
Features
Multi-source ingestion: Twitter/X (academic API), Reddit, RSS feeds, OpenAQ, NOAA alerts.
Enrichment pipeline: language detection, sentiment analysis (DistilBERT), geocoding (Nominatim), entity extraction (spaCy), source-score calculation.
Alert engine: YAML-defined rules (e.g., volume spikes) with email/webhook notifications.
Report generation: PDF/CSV/JSON exports with maps and source hashes.
Demo UI: Streamlit app for quick visual inspection.
Dockerised: easy reproducibility with `docker compose up`.
CI/CD: GitHub Actions workflow runs tests and builds a Docker image.
Quick Start
Clone the repo
```bash
   git clone https://github.com/<your-username>/osint-enricher.git
   cd osint-enricher
   ```
Configure environment
Copy the example files and add your API keys:
```bash
   cp config/rules.yaml.example config/rules.yaml
   cp .env.example .env
   # edit .env to insert your Twitter academic bearer token, Reddit credentials, etc.
   ```
Start supporting services
```bash
   docker compose up -d   # starts MinIO (S3-compatible storage) and Redis (cache)
   ```
Run the pipeline
```bash
   # Ingest last 30 minutes from Twitter & Reddit
   python -m src.connectors.run --sources twitter,reddit --since 30m

   # Enrich the raw data
   python -m src.enrichment.run --input data/raw/ --output data/enriched/

   # Check alert rules and send notifications
   python -m src.alerting.run --config config/rules.yaml

   # Generate a PDF report for the last 2 hours
   python -m src.report.run --format pdf --since 2h --output reports/report_$(date +%F).pdf

   # (Optional) Launch the demo UI
   streamlit run src/app.py
   ```
Project Structure
```
osint-enricher/
+-- src/
    +-- connectors/      # Ingestion modules (twitter.py, reddit.py,  )
    +-- enrichment/      # Normalisation & enrichment (geocode, sentiment,  )
    +-- alerting/        # Rule engine & notifiers
    +-- storage/         # Abstraction over MinIO / local FS
    +-- api/             # FastAPI endpoints (optional)
+-- config/
    +-- rules.yaml.example   # Example alert rules
    +-- logging.yaml
+-- data/                 # raw/, enriched/, reports/ (git-ignored)
+-- tests/                # Pytest suite
+-- docs/                 # Documentation, diagrams
+-- Dockerfile            # Builds the runtime image
+-- docker-compose.yml    # MinIO + Redis + app
+-- requirements.txt      # Python dependencies
+-- pyproject.toml        # Package metadata
+-- .gitignore
+-- README.md
```
License
MIT   see the `LICENSE` file.
Disclaimer
This tool is intended for research, journalism, risk-management, and public-interest OSINT only. It must not be used for harassment, doxxing, or any unlawful surveillance. All data collected must be publicly available; personal identifiers are pseudonymised before storage to comply with GDPR-like regulations.
---
Happy hunting!
o s i n t - e n r i c h e r
