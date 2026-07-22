"""Abstract storage layer."""
from abc import ABC, abstractmethod
from typing import Iterable

class BaseStorage(ABC):
    @abstractmethod
    def put_object(self, bucket: str, key: str, data: bytes) -> None:
        """Store raw bytes under bucket/key."""
        raise NotImplementedError

    @abstractmethod
    def get_object(self, bucket: str, key: str) -> bytes:
        """Retrieve raw bytes."""
        raise NotImplementedError

    @abstractmethod
    def list_objects(self, bucket: str, prefix: str = "") -> Iterable[str]:
        """Yield object keys under bucket with optional prefix."""
        raise NotImplementedError

    @abstractmethod
    def delete_object(self, bucket: str, key: str) -> None:
        """Delete an object."""
        raise NotImplementedError
