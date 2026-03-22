from __future__ import annotations

from app.core.config import STORAGE_BACKEND
from app.services.storage.local_storage import LocalStorageService


def get_storage_service():
    if STORAGE_BACKEND == "local":
        return LocalStorageService()
    if STORAGE_BACKEND == "r2":
        from app.services.storage.r2 import R2StorageService

        return R2StorageService()

    raise ValueError(f"Unsupported storage backend: {STORAGE_BACKEND}")
