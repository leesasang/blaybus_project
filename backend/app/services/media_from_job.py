from __future__ import annotations

from sqlalchemy.orm import Session

from app.db.models import Job, MediaAsset


def create_media_from_job_result(db: Session, *, job: Job) -> None:
    if not job.output_payload or not isinstance(job.output_payload, dict):
        return

    outputs = job.output_payload.get("outputs")
    if not isinstance(outputs, list):
        return

    existing = db.query(MediaAsset).filter(MediaAsset.job_id == job.id).count()
    if existing > 0:
        return

    for output in outputs:
        db.add(
            MediaAsset(
                user_id=job.user_id,
                project_id=job.project_id,
                job_id=job.id,
                media_type=output.get("media_type", "image"),
                origin_type="generated",
                filename=output["filename"],
                original_filename=output.get("original_filename"),
                content_type=output.get("content_type", "application/octet-stream"),
                size_bytes=output.get("size_bytes"),
                storage_provider=output.get("storage_provider", "local"),
                storage_path=output["storage_path"],
                public_url=output.get("public_url"),
                thumbnail_url=output.get("thumbnail_url"),
                status="ready",
                width=output.get("width"),
                height=output.get("height"),
                duration_seconds=output.get("duration_seconds"),
                prompt_text=(job.input_payload or {}).get("prompt"),
                title=output.get("title"),
                description=output.get("description"),
                visibility=output.get("visibility", "private"),
                error_message=None,
            )
        )

    db.commit()
