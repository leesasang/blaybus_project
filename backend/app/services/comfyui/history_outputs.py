"""ComfyUI /history 응답에서 저장된 파일 메타를 수집합니다."""

from __future__ import annotations

from typing import Any


def collect_files_from_history(history_entry: dict[str, Any]) -> list[dict[str, Any]]:
    """노드 출력에 포함된 images / gifs 등에서 filename·subfolder·type을 모읍니다."""
    out: list[dict[str, Any]] = []
    outputs = history_entry.get("outputs") or {}
    for node_id, node_out in outputs.items():
        if not isinstance(node_out, dict):
            continue
        for key in ("images", "gifs", "videos", "audio"):
            items = node_out.get(key)
            if not items:
                continue
            if not isinstance(items, list):
                continue
            for item in items:
                if isinstance(item, dict) and item.get("filename"):
                    out.append(
                        {
                            "filename": item["filename"],
                            "subfolder": item.get("subfolder", ""),
                            "folder_type": item.get("type", "output"),
                            "node_id": str(node_id),
                            "kind": key,
                        }
                    )
    return out


def guess_content_type(filename: str) -> str:
    lower = filename.lower()
    if lower.endswith(".png"):
        return "image/png"
    if lower.endswith((".jpg", ".jpeg")):
        return "image/jpeg"
    if lower.endswith(".webp"):
        return "image/webp"
    if lower.endswith(".gif"):
        return "image/gif"
    if lower.endswith(".webm"):
        return "video/webm"
    if lower.endswith(".mp4"):
        return "video/mp4"
    return "application/octet-stream"


def guess_media_type(filename: str) -> str:
    lower = filename.lower()
    if lower.endswith((".mp4", ".webm", ".gif")):
        return "video"
    return "image"
