# OSINT Enricher

OSINT Enricher is a local-first toolkit for collecting public data, enriching it, evaluating alert rules and generating reports. It exposes a FastAPI health endpoint and can be run with Docker Compose.

> Use it only for lawful research, journalism, risk management and public-interest OSINT. Do not use it for harassment, doxxing or unlawful surveillance.

## What works

- Connectors for RSS, NOAA alerts, OpenAQ, Twitter/X and Reddit.
- JSON/JSONL ingestion and Parquet enrichment output.
- Language, sentiment, entity, geocoding and source-credibility enrichment.
- YAML volume-spike rules.
- JSON, CSV and PDF reports.
- FastAPI health endpoint and Streamlit inspection UI.
- Automated tests, package checks, Docker build and container smoke test in GitHub Actions.

High-accuracy sentiment and entity extraction use optional transformer and spaCy backends. Without them, deterministic lightweight fallbacks keep the pipeline usable offline.

## Guida rapida (in italiano)

### Avvio con Docker Compose

```bash
git clone https://github.com/gnudrus/osint-enricher.git
cd osint-enricher
cp .env.example .env
cp config/rules.yaml.example config/rules.yaml
docker compose up --build -d
curl --fail http://localhost:8000/health
```

Il risultato atteso è:

```json
{"status":"ok","version":"0.2.0"}
```

MinIO è disponibile su `http://localhost:9001`, Redis sulla porta `6379` e l'API su `http://localhost:8000`.

### Avvio locale

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
uvicorn src.api.main:app --reload
```

Per installare anche i backend NLP ad alta accuratezza:

```bash
python -m pip install -e ".[nlp]"
python -m spacy download en_core_web_sm
```

### Pipeline di esempio

```bash
# Ingestione RSS senza credenziali
RSS_FEEDS="https://feeds.bbci.co.uk/news/world/rss.xml" \
  python -m src.connectors.run --sources rss --since 30m --output data/raw

# Enrichment e output Parquet
python -m src.enrichment.run --input data/raw --output data/enriched

# Valutazione delle regole su JSONL
python -m src.alerting.run --config config/rules.yaml --input data/raw

# Report
python -m src.report.run --input data/enriched --format csv --output reports/report.csv

# UI opzionale
streamlit run src/app.py
```

Twitter e Reddit richiedono le credenziali indicate in `.env.example`. I connettori pubblici e i test non richiedono segreti.

## Verifica del progetto

```bash
python -m compileall -q src tests
python -m pytest -q --cov=src
docker compose config --quiet
docker build -t osint-enricher .
```

## Struttura

```text
src/connectors/   acquisizione delle fonti
src/enrichment/   trasformazioni e NLP
src/alerting/     regole e notificatori
src/storage/      filesystem locale e MinIO/S3
src/report/       esportazione JSON, CSV e PDF
src/api/          API FastAPI
tests/            test automatici
```

## Licenza

MIT. Vedi [LICENSE](LICENSE).
