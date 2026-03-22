from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.models import Job, MediaAsset, MediaStat
from app.schemas.media import MediaCreate, MediaUpdate


def create_media(db: Session, *, media_in: MediaCreate, user_id: UUID) -> MediaAsset:
    media = MediaAsset(
        user_id=user_id,
        project_id=media_in.project_id,
        job_id=media_in.job_id,
        media_type=media_in.media_type,
        origin_type=media_in.origin_type,
        filename=media_in.filename,
        original_filename=media_in.original_filename,
        content_type=media_in.content_type,
        size_bytes=media_in.size_bytes,
        storage_provider=media_in.storage_provider,
        storage_path=media_in.storage_path,
        public_url=media_in.public_url,
        thumbnail_url=media_in.thumbnail_url,
        status=media_in.status,
        width=media_in.width,
        height=media_in.height,
        duration_seconds=media_in.duration_seconds,
        prompt_text=media_in.prompt_text,
        title=media_in.title,
        description=media_in.description,
        visibility=media_in.visibility,
        error_message=media_in.error_message,
    )
    db.add(media)
    db.commit()
    db.refresh(media)
    return media


def get_media_by_id(db: Session, media_id: UUID) -> MediaAsset | None:
    stmt = select(MediaAsset).where(
        MediaAsset.id == media_id,
        MediaAsset.deleted_at.is_(None),
    )
    return db.scalar(stmt)


def get_media_by_job_id(db: Session, *, job_id: UUID) -> MediaAsset | None:
    stmt = select(MediaAsset).where(
        MediaAsset.job_id == job_id,
        MediaAsset.deleted_at.is_(None),
    )
    return db.scalar(stmt)


def create_media_from_image_job_result(db: Session, *, job: Job) -> MediaAsset:
    if job.output_payload is None:
        raise ValueError("Job output_payload is required")

    existing_media = get_media_by_job_id(db, job_id=job.id)
    if existing_media is not None:
        return existing_media

    output: dict[str, Any] = job.output_payload or {}
    input_payload: dict[str, Any] = job.input_payload or {}

    filename = output.get("filename")
    storage_path = output.get("storage_path")

    if not filename:
        raise ValueError("output_payload.filename is required")

    if not storage_path:
        raise ValueError("output_payload.storage_path is required")

    media = MediaAsset(
        user_id=job.user_id,
        project_id=job.project_id,
        job_id=job.id,
        media_type="image",
        origin_type="generated",
        filename=filename,
        original_filename=output.get("original_filename"),
        content_type=output.get("content_type", "image/png"),
        size_bytes=output.get("size_bytes"),
        storage_provider=output.get("storage_provider", "firebase"),
        storage_path=storage_path,
        public_url=output.get("public_url"),
        thumbnail_url=output.get("thumbnail_url"),
        status=output.get("media_status", "ready"),
        width=output.get("width"),
        height=output.get("height"),
        duration_seconds=output.get("duration_seconds"),
        prompt_text=input_payload.get("prompt"),
        title=output.get("title"),
        description=output.get("description"),
        visibility=output.get("visibility", "private"),
        error_message=None,
    )

    db.add(media)
    db.commit()
    db.refresh(media)
    return media


def get_media_list_by_project(
    db: Session,
    project_id: UUID,
    skip: int = 0,
    limit: int = 20,
) -> tuple[list[MediaAsset], int]:
    conditions = [
        MediaAsset.project_id == project_id,
        MediaAsset.deleted_at.is_(None),
    ]

    total_stmt = select(func.count()).select_from(MediaAsset).where(*conditions)
    total = db.scalar(total_stmt) or 0

    stmt = (
        select(MediaAsset)
        .where(*conditions)
        .order_by(MediaAsset.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    items = list(db.scalars(stmt).all())

    return items, total


def update_media(
    db: Session,
    media: MediaAsset,
    media_in: MediaUpdate,
) -> MediaAsset:
    update_data = media_in.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(media, field, value)

    db.add(media)
    db.commit()
    db.refresh(media)
    return media


def get_media_stats(db: Session, media_asset_id: UUID) -> MediaStat | None:
    stmt = select(MediaStat).where(MediaStat.media_asset_id == media_asset_id)
    return db.scalar(stmt)


def ensure_media_stats(db: Session, media_asset_id: UUID) -> MediaStat:
    stmt = select(MediaStat).where(MediaStat.media_asset_id == media_asset_id)
    stats = db.scalar(stmt)

    if stats is None:
        stats = MediaStat(
            media_asset_id=media_asset_id,
            view_count=0,
            like_count=0,
            comment_count=0,
            bookmark_count=0,
        )
        db.add(stats)
        db.flush()

    return stats


def increment_media_view_count(db: Session, media_asset_id: UUID) -> MediaStat:
    stats = ensure_media_stats(db=db, media_asset_id=media_asset_id)
    stats.view_count += 1
    db.add(stats)
    db.commit()
    db.refresh(stats)
    return stats


def increment_media_like_count(db: Session, media_asset_id: UUID) -> MediaStat:
    stats = ensure_media_stats(db=db, media_asset_id=media_asset_id)
    stats.like_count += 1
    db.add(stats)
    db.commit()
    db.refresh(stats)
    return stats


def decrement_media_like_count(db: Session, media_asset_id: UUID) -> MediaStat:
    stats = ensure_media_stats(db=db, media_asset_id=media_asset_id)
    if stats.like_count > 0:
        stats.like_count -= 1
    db.add(stats)
    db.commit()
    db.refresh(stats)
    return stats


def increment_media_comment_count(db: Session, media_asset_id: UUID) -> MediaStat:
    stats = ensure_media_stats(db=db, media_asset_id=media_asset_id)
    stats.comment_count += 1
    db.add(stats)
    db.commit()
    db.refresh(stats)
    return stats


def decrement_media_comment_count(db: Session, media_asset_id: UUID) -> MediaStat:
    stats = ensure_media_stats(db=db, media_asset_id=media_asset_id)
    if stats.comment_count > 0:
        stats.comment_count -= 1
    db.add(stats)
    db.commit()
    db.refresh(stats)
    return stats
