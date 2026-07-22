"""Reddit connector using PRAW."""
import os
from typing import Iterable, Dict, Any
import praw
from .base import BaseConnector


class RedditConnector(BaseConnector):
    def __init__(
        self,
        client_id: str | None = None,
        client_secret: str | None = None,
        user_agent: str = "osint-enricher/0.1",
    ):
        self.client_id = client_id or os.getenv("REDDIT_CLIENT_ID")
        self.client_secret = client_secret or os.getenv("REDDIT_CLIENT_SECRET")
        if not self.client_id or not self.client_secret:
            raise ValueError("Reddit credentials missing")
        self.reddit = praw.Reddit(
            client_id=self.client_id,
            client_secret=self.client_secret,
            user_agent=user_agent,
        )

    def fetch(self, since: str) -> Iterable[Dict[str, Any]]:
        # Stub implementation
        yield {}
