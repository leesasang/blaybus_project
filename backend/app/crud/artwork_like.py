from __future__ import annotations

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.crud.media import decrement_media_like_count, increment_media_like_count
from app.db.models import Like


def create_like(db: Session, user_id: UUID, media_asset_id: UUID) -> Like | None:
    existing = db.scalar(
        select(Like).where(
            Like.user_id == user_id,
            Like.media_asset_id == media_asset_id,
        )
    )
    if existing is not None:
        return existing

    like = Like(
        user_id=user_id,
        media_asset_id=media_asset_id,
    )
    db.add(like)
    db.commit()
    db.refresh(like)

    increment_media_like_count(db=db, media_asset_id=media_asset_id)
    return like


def delete_like(db: Session, user_id: UUID, media_asset_id: UUID) -> bool:
    existing = db.scalar(
        select(Like).where(
            Like.user_id == user_id,
            Like.media_asset_id == media_asset_id,
        )
    )
    if existing is None:
        return False

    db.delete(existing)
    db.commit()

    decrement_media_like_count(db=db, media_asset_id=media_asset_id)
    return True


def get_like_count(db: Session, media_asset_id: UUID) -> int:
    stmt = select(func.count()).select_from(Like).where(
        Like.media_asset_id == media_asset_id
    )
    return db.scalar(stmt) or 0
