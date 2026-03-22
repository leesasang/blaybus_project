from __future__ import annotations

from abc import ABC, abstractmethod


class StorageService(ABC):
    @abstractmethod
    def save_file(self, *, data: bytes, relative_path: str) -> dict:
        raise NotImplementedError
