from __future__ import annotations

import os
import subprocess
import threading
from datetime import datetime, timezone
from pathlib import Path
from uuid import UUID

from sqlalchemy.orm import Session

from app.core.config import (
    COMFYUI_IMAGE_WORKFLOW_PATH,
    COMFYUI_MAX_WAIT_SECONDS,
    COMFYUI_VIDEO_PIPELINE_WORKFLOW_PATH,
    HF_TOKEN,
    PLOT_BASE_MODEL_LOCAL,
    PLOT_GENERATION_CLI,
    PLOT_GENERATION_PYTHON,
)
from app.db.database import SessionLocal
from app.db.models import Job, Project
from app.services.comfyui.client import ComfyUIClient
from app.services.comfyui.history_outputs import (
    collect_files_from_history,
    guess_content_type,
    guess_media_type,
)
from app.services.comfyui.ui_workflow import (
    load_ui_workflow,
    ui_to_prompt,
    patch_hackathon_image_prompt,
    patch_hackathon_image_video_prompt,
)
from app.services.media_from_job import create_media_from_job_result
from app.services.storage.factory import get_storage_service


def schedule_job_processing(job_id: UUID) -> None:
    def _run() -> None:
        db = SessionLocal()
        try:
            process_job(db, job_id)
        finally:
            db.close()

    threading.Thread(target=_run, daemon=True).start()


def process_job(db: Session, job_id: UUID) -> None:
    job = db.query(Job).filter(Job.id == job_id).first()
    if job is None:
        return

    if job.job_type == "image_to_video":
        _fail_job(
            db,
            job,
            "image_to_video는 MVP에서 단일 이미지 업로드·LoadImage 분기가 없어 지원하지 않습니다. "
            "text-to-image-to-video 워크플로를 사용하세요.",
        )
        return

    job.status = "running"
    job.started_at = datetime.now(timezone.utc)
    base_out = job.output_payload if isinstance(job.output_payload, dict) else {}
    job.output_payload = {
        **base_out,
        "progress": {"stage": "running", "percent": 5},
    }
    job.error_message = None
    db.add(job)
    db.commit()

    try:
        if job.job_type == "plot_generation":
            _run_plot(db, job)
        elif job.job_type == "text_to_image":
            _run_text_to_image(db, job)
        elif job.job_type == "text_to_image_to_video":
            _run_text_to_image_to_video(db, job)
        else:
            _fail_job(db, job, f"unsupported job type: {job.job_type}")
    except Exception as exc:
        _fail_job(db, job, str(exc))


def _fail_job(db: Session, job: Job, message: str) -> None:
    job.status = "failed"
    job.error_message = message
    job.completed_at = datetime.now(timezone.utc)
    op = job.output_payload if isinstance(job.output_payload, dict) else {}
    job.output_payload = {**op, "progress": {"stage": "failed", "percent": 100}}
    db.add(job)
    db.commit()


def _complete_generation_job(db: Session, job: Job, output_payload: dict) -> None:
    job.status = "completed"
    job.completed_at = datetime.now(timezone.utc)
    job.output_payload = output_payload
    job.error_message = None
    db.add(job)
    db.commit()
    db.refresh(job)
    create_media_from_job_result(db, job=job)


def _run_plot(db: Session, job: Job) -> None:
    payload = job.input_payload or {}
    prompt = payload.get("prompt")
    if not prompt:
        raise ValueError("plot_generation requires prompt")

    cli_path = Path(PLOT_GENERATION_CLI)
    if not cli_path.is_file():
        raise FileNotFoundError(
            f"플롯 생성 스크립트를 찾을 수 없습니다: {cli_path}. "
            "환경 변수 PLOT_GENERATION_CLI로 경로를 지정하세요."
        )

    cmd = [PLOT_GENERATION_PYTHON, str(cli_path), "--prompt", prompt]
    plot_env = os.environ.copy()
    plot_env.setdefault("PYTHONWARNINGS", "ignore")
    plot_env.setdefault("TOKENIZERS_PARALLELISM", "false")
    if HF_TOKEN:
        plot_env["HF_TOKEN"] = HF_TOKEN
        plot_env["HUGGING_FACE_HUB_TOKEN"] = HF_TOKEN
    if PLOT_BASE_MODEL_LOCAL:
        plot_env["PLOT_BASE_MODEL_LOCAL"] = PLOT_BASE_MODEL_LOCAL
    proc = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=600,
        env=plot_env,
    )
    if proc.returncode != 0:
        err = (proc.stderr or proc.stdout or "").strip()
        raise RuntimeError(f"plot_generation 실패: {err[:2500]}")

    plot_text = (proc.stdout or "").strip()
    if not plot_text:
        raise RuntimeError("plot_generation 빈 출력")

    project = db.query(Project).filter(Project.id == job.project_id).first()
    if project:
        project.plot_text = plot_text
        db.add(project)

    job.output_payload = {
        "progress": {"stage": "completed", "percent": 100},
        "plot_text": plot_text,
    }
    job.status = "completed"
    job.completed_at = datetime.now(timezone.utc)
    job.error_message = None
    db.add(job)
    db.commit()


def _run_text_to_image(db: Session, job: Job) -> None:
    payload = job.input_payload or {}
    prompt = payload.get("prompt")
    if not prompt:
        raise ValueError("prompt required")

    negative = payload.get("negative_prompt") or ""
    width = int(payload.get("width") or 512)
    height = int(payload.get("height") or 512)
    seed = payload.get("seed")
    batch_size = int(payload.get("batch_size") or 1)
    save_prefix = payload.get("save_prefix") or "ComfyUI"

    ui = load_ui_workflow(Path(COMFYUI_IMAGE_WORKFLOW_PATH))
    wf = ui_to_prompt(ui)
    patch_hackathon_image_prompt(
        wf,
        positive=prompt,
        negative=negative,
        width=width,
        height=height,
        seed=seed,
        batch_size=batch_size,
        save_prefix=save_prefix,
    )

    client = ComfyUIClient()
    prompt_id = client.submit_workflow(wf)
    history_entry = client.wait_until_done(
        prompt_id,
        max_wait_seconds=COMFYUI_MAX_WAIT_SECONDS,
    )
    files = collect_files_from_history(history_entry)
    if not files:
        raise RuntimeError("ComfyUI 결과에서 파일을 찾지 못했습니다.")

    storage = get_storage_service()
    outputs = []
    for meta in files:
        data = client.download_artifact(
            filename=meta["filename"],
            subfolder=meta["subfolder"],
            folder_type=meta["folder_type"],
        )
        rel = f"generated/{job.user_id}/{job.id}/{meta['filename']}"
        saved = storage.save_file(data=data, relative_path=rel)
        outputs.append(
            {
                "filename": meta["filename"],
                "original_filename": meta["filename"],
                "content_type": guess_content_type(meta["filename"]),
                "media_type": guess_media_type(meta["filename"]),
                "storage_provider": saved["storage_provider"],
                "storage_path": saved["storage_path"],
                "public_url": saved["public_url"],
                "size_bytes": saved["size_bytes"],
            }
        )

    out_payload = {
        "progress": {"stage": "completed", "percent": 100},
        "outputs": outputs,
    }
    _complete_generation_job(db, job, out_payload)


def _run_text_to_image_to_video(db: Session, job: Job) -> None:
    payload = job.input_payload or {}
    prompt = payload.get("prompt")
    if not prompt:
        raise ValueError("prompt required")

    ui = load_ui_workflow(Path(COMFYUI_VIDEO_PIPELINE_WORKFLOW_PATH))
    wf = ui_to_prompt(ui)
    patch_hackathon_image_video_prompt(
        wf,
        positive=prompt,
        negative=payload.get("negative_prompt") or "",
        image_width=int(payload.get("image_width") or 512),
        image_height=int(payload.get("image_height") or 512),
        image_seed=payload.get("image_seed"),
        image_batch_size=int(payload.get("image_batch_size") or 1),
        video_width=int(payload.get("video_width") or 1024),
        video_height=int(payload.get("video_height") or 576),
        video_frames=int(payload.get("video_frames") or 25),
        motion_bucket_id=int(payload.get("motion_bucket_id") or 127),
        video_fps=int(payload.get("video_fps") or 10),
        augmentation_level=float(payload.get("augmentation_level") or 0.0),
        video_noise_seed=payload.get("video_noise_seed"),
        image_save_prefix=payload.get("image_save_prefix") or "ComfyUI",
        video_save_prefix=payload.get("video_save_prefix") or "AnimateDiff",
        output_frame_rate=int(payload.get("output_frame_rate") or 8),
        output_format=payload.get("output_format") or "image/gif",
    )

    client = ComfyUIClient()
    prompt_id = client.submit_workflow(wf)
    history_entry = client.wait_until_done(
        prompt_id,
        max_wait_seconds=COMFYUI_MAX_WAIT_SECONDS,
    )
    files = collect_files_from_history(history_entry)
    if not files:
        raise RuntimeError("ComfyUI 결과에서 파일을 찾지 못했습니다.")

    storage = get_storage_service()
    outputs = []
    for meta in files:
        data = client.download_artifact(
            filename=meta["filename"],
            subfolder=meta["subfolder"],
            folder_type=meta["folder_type"],
        )
        rel = f"generated/{job.user_id}/{job.id}/{meta['filename']}"
        saved = storage.save_file(data=data, relative_path=rel)
        outputs.append(
            {
                "filename": meta["filename"],
                "original_filename": meta["filename"],
                "content_type": guess_content_type(meta["filename"]),
                "media_type": guess_media_type(meta["filename"]),
                "storage_provider": saved["storage_provider"],
                "storage_path": saved["storage_path"],
                "public_url": saved["public_url"],
                "size_bytes": saved["size_bytes"],
            }
        )

    out_payload = {
        "progress": {"stage": "completed", "percent": 100},
        "outputs": outputs,
    }
    _complete_generation_job(db, job, out_payload)
