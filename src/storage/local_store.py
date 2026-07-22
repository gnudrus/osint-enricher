"""Local filesystem storage (for development)."""
import os
from pathlib import Path
from .base import BaseStorage

class LocalStore(BaseStorage):
    def __init__(self, root_path: str | os.PathLike = "data/storage"):
        self.root = Path(root_path)
        self.root.mkdir(parents=True, exist_ok=True)

    def _full_path(self, bucket: str, key: str) -> Path:
        return self.root / bucket / key

    def put_object(self, bucket: str, key: str, data: bytes) -> None:
        path = self._full_path(bucket, key)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)

    def get_object(self, bucket: str, key: str) -> bytes:
        path = self._full_path(bucket, key)
        return path.read_bytes()

    def list_objects(self, bucket: str, prefix: str = ""):
        base = self.root / bucket / prefix
        if not base.exists():
            return
        for root, _, files in os.walk(base):
            for f in files:
                full = Path(root) / f
                rel = os.path.relpath(full, self.root)
                yield str(rel).replace(os.sep, "/")

    def delete_object(self, bucket: str, key: str) -> None:
        path = self._full_path(bucket, key)
        if path.exists():
            path.unlink()
