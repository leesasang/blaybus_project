from __future__ import annotations

from pathlib import Path

from app.core.config import PUBLIC_BASE_URL, STORAGE_ROOT
from app.services.storage.base import StorageService


class LocalStorageService(StorageService):
    def __init__(self) -> None:
        self.root = Path(STORAGE_ROOT)

    def save_file(self, *, data: bytes, relative_path: str) -> dict:
        full_path = self.root / relative_path
        full_path.parent.mkdir(parents=True, exist_ok=True)
        full_path.write_bytes(data)

        relative_url_path = relative_path.replace("\\", "/")
        normalized_storage_path = str(full_path).replace("\\", "/")
        public_url = f"{PUBLIC_BASE_URL}/storage/{relative_url_path}"

        return {
            "storage_provider": "local",
            "storage_path": normalized_storage_path,
            "public_url": public_url,
            "size_bytes": len(data),
        }
