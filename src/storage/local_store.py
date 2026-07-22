"""Local filesystem storage backend."""

from __future__ import annotations

import os
from pathlib import Path

from .base import BaseStorage


class LocalStore(BaseStorage):
    def __init__(self, root_path: str | os.PathLike = "data/storage"):
        self.root = Path(root_path).resolve()
        self.root.mkdir(parents=True, exist_ok=True)

    def _full_path(self, bucket: str, key: str) -> Path:
        if not bucket or not key:
            raise ValueError("bucket and key are required")
        path = (self.root / bucket / key).resolve()
        if not path.is_relative_to(self.root):
            raise ValueError("bucket/key must remain inside the storage root")
        return path

    def put_object(self, bucket: str, key: str, data: bytes) -> None:
        path = self._full_path(bucket, key)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)

    def get_object(self, bucket: str, key: str) -> bytes:
        return self._full_path(bucket, key).read_bytes()

    def list_objects(self, bucket: str, prefix: str = ""):
        bucket_root = (self.root / bucket).resolve()
        base = (bucket_root / prefix).resolve()
        if not base.is_relative_to(bucket_root):
            raise ValueError("prefix must remain inside the bucket")
        if not base.exists():
            return
        for root, _, files in os.walk(base):
            for filename in files:
                yield (Path(root) / filename).relative_to(bucket_root).as_posix()

    def delete_object(self, bucket: str, key: str) -> None:
        path = self._full_path(bucket, key)
        if path.exists():
            path.unlink()
