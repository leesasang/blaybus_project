"""ComfyUI 프론트엔드 형식(workflow JSON)을 /prompt API용 딕셔너리로 변환하고 프롬프트를 주입합니다."""

from __future__ import annotations

import copy
import json
import random
from pathlib import Path
from typing import Any

_cache: dict[str, dict[str, Any]] = {}


def load_ui_workflow(path: Path) -> dict[str, Any]:
    key = str(path.resolve())
    if key not in _cache:
        with open(path, encoding="utf-8") as f:
            _cache[key] = json.load(f)
    return copy.deepcopy(_cache[key])


def ui_to_prompt(ui: dict[str, Any]) -> dict[str, Any]:
    links_by_id = {link[0]: link for link in ui["links"]}
    prompt: dict[str, Any] = {}
    for node in ui["nodes"]:
        nid = str(node["id"])
        class_type = node["type"]
        inputs_out: dict[str, Any] = {}
        inputs_def = node.get("inputs") or []
        wv = node.get("widgets_values")
        if isinstance(wv, dict):
            widget_queue = None
        else:
            widget_queue = list(wv or [])

        for inp in inputs_def:
            name = inp["name"]
            link_id = inp.get("link")
            if link_id is not None:
                link = links_by_id.get(link_id)
                if not link:
                    continue
                _, src_node, src_slot, _, _, _ = link
                inputs_out[name] = [str(src_node), src_slot]
            else:
                if inp.get("widget") is None and inp.get("shape") is not None:
                    continue
                if isinstance(wv, dict):
                    if name in wv and name not in ("videopreview",):
                        inputs_out[name] = wv[name]
                else:
                    if widget_queue:
                        inputs_out[name] = widget_queue.pop(0)

        prompt[nid] = {"class_type": class_type, "inputs": inputs_out}
    return prompt


def _resolve_seed(value: int | None) -> int:
    if value is None:
        return random.randint(1, 2**31 - 1)
    return value


def patch_hackathon_image_prompt(
    prompt: dict[str, Any],
    *,
    positive: str,
    negative: str,
    width: int,
    height: int,
    seed: int | None,
    batch_size: int = 1,
    save_prefix: str = "ComfyUI",
) -> None:
    """hackathon_image_generation_model.json 기준 노드 ID."""
    if "4" in prompt:
        prompt["4"]["inputs"]["text"] = positive
    if "5" in prompt:
        prompt["5"]["inputs"]["text"] = negative
    if "10" in prompt:
        prompt["10"]["inputs"]["width"] = width
        prompt["10"]["inputs"]["height"] = height
        prompt["10"]["inputs"]["batch_size"] = batch_size
    if "11" in prompt:
        prompt["11"]["inputs"]["seed"] = _resolve_seed(seed)
    if "12" in prompt:
        prompt["12"]["inputs"]["filename_prefix"] = save_prefix


def patch_hackathon_image_video_prompt(
    prompt: dict[str, Any],
    *,
    positive: str,
    negative: str,
    image_width: int,
    image_height: int,
    image_seed: int | None,
    image_batch_size: int = 1,
    video_width: int,
    video_height: int,
    video_frames: int,
    motion_bucket_id: int,
    video_fps: int,
    augmentation_level: float,
    video_noise_seed: int | None,
    image_save_prefix: str = "ComfyUI",
    video_save_prefix: str = "AnimateDiff",
    output_frame_rate: int = 8,
    output_format: str = "image/gif",
) -> None:
    """hackathon_image,video_generation.json 기준 노드 ID."""
    if "2" in prompt:
        prompt["2"]["inputs"]["text"] = positive
    if "3" in prompt:
        prompt["3"]["inputs"]["text"] = negative
    if "4" in prompt:
        prompt["4"]["inputs"]["width"] = image_width
        prompt["4"]["inputs"]["height"] = image_height
        prompt["4"]["inputs"]["batch_size"] = image_batch_size
    if "5" in prompt:
        prompt["5"]["inputs"]["seed"] = _resolve_seed(image_seed)
    if "7" in prompt:
        prompt["7"]["inputs"]["width"] = video_width
        prompt["7"]["inputs"]["height"] = video_height
        prompt["7"]["inputs"]["video_frames"] = video_frames
        prompt["7"]["inputs"]["motion_bucket_id"] = motion_bucket_id
        prompt["7"]["inputs"]["fps"] = video_fps
        prompt["7"]["inputs"]["augmentation_level"] = augmentation_level
    if "8" in prompt:
        prompt["8"]["inputs"]["filename_prefix"] = image_save_prefix
    if "11" in prompt:
        prompt["11"]["inputs"]["noise_seed"] = _resolve_seed(video_noise_seed)
    if "13" in prompt:
        ins = prompt["13"]["inputs"]
        ins["filename_prefix"] = video_save_prefix
        ins["frame_rate"] = float(output_frame_rate)
        ins["format"] = output_format
