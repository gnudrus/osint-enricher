"""FastAPI app exposing enrichment results."""
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List, Optional
import uvicorn

app = FastAPI(title="OSINT Enricher API", version="0.1.0")

class Event(BaseModel):
    id: str
    source: str
    text: str
    timestamp: str
    sentiment_label: Optional[str] = None
    sentiment_score: Optional[float] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    entities: List[dict] = []
    source_score: Optional[float] = None

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/events", response_model=List[Event])
def get_events(limit: int = 100):
    # Placeholder: return empty list; in a real app, query storage
    return []

def run(host: str = "0.0.0.0", port: int = 8000):
    uvicorn.run("src.api.main:app", host=host, port=port, reload=False)

if __name__ == "__main__":
    run()
