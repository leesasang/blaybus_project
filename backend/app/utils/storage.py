from __future__ import annotations

import uuid
from pathlib import Path


def build_storage_path(project_id: str, original_filename: str, media_dir: str = "images") -> str:
    ext = Path(original_filename).suffix.lower() or ".bin"
    return f"projects/{project_id}/{media_dir}/{uuid.uuid4()}{ext}"
