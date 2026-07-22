"""FastAPI application for OSINT Enricher."""

from __future__ import annotations

from typing import List, Optional

import uvicorn
from fastapi import FastAPI, Query
from pydantic import BaseModel, Field

VERSION = "0.2.0"
app = FastAPI(title="OSINT Enricher API", version=VERSION)


class Event(BaseModel):
    id: str
    source: str
    text: str
    timestamp: str
    sentiment_label: Optional[str] = None
    sentiment_score: Optional[float] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    entities: List[dict] = Field(default_factory=list)
    source_score: Optional[float] = None


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok", "version": VERSION}


@app.get("/events", response_model=List[Event])
def get_events(limit: int = Query(default=100, ge=1, le=1000)) -> list[Event]:
    """Return stored events. The storage adapter will be wired here in a future release."""
    return []


def run(host: str = "0.0.0.0", port: int = 8000) -> None:
    uvicorn.run("src.api.main:app", host=host, port=port, reload=False)


if __name__ == "__main__":
    run()
