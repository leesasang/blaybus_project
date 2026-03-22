from __future__ import annotations

from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.crud.media import decrement_media_comment_count, increment_media_comment_count
from app.db.models import Comment
from app.schemas.comment import CommentUpdate


def create_comment(
    db: Session,
    user_id: UUID,
    media_asset_id: UUID,
    content: str,
) -> Comment:
    comment = Comment(
        user_id=user_id,
        media_asset_id=media_asset_id,
        content=content,
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)

    increment_media_comment_count(db=db, media_asset_id=comment.media_asset_id)
    return comment


def get_comment_by_id(db: Session, comment_id: UUID) -> Comment | None:
    stmt = select(Comment).where(
        Comment.id == comment_id,
        Comment.deleted_at.is_(None),
    )
    return db.scalar(stmt)


def get_comments_by_media(
    db: Session,
    media_asset_id: UUID,
    skip: int = 0,
    limit: int = 20,
) -> tuple[list[Comment], int]:
    conditions = [
        Comment.media_asset_id == media_asset_id,
        Comment.deleted_at.is_(None),
    ]

    total_stmt = select(func.count()).select_from(Comment).where(*conditions)
    total = db.scalar(total_stmt) or 0

    stmt = (
        select(Comment)
        .where(*conditions)
        .order_by(Comment.created_at.asc())
        .offset(skip)
        .limit(limit)
    )
    items = list(db.scalars(stmt).all())
    return items, total


def update_comment(
    db: Session,
    comment: Comment,
    comment_in: CommentUpdate,
) -> Comment:
    update_data = comment_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(comment, field, value)

    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment


def soft_delete_comment(db: Session, comment: Comment) -> Comment:
    from sqlalchemy.sql import func

    comment.deleted_at = func.now()
    db.add(comment)
    db.commit()
    db.refresh(comment)

    decrement_media_comment_count(db=db, media_asset_id=comment.media_asset_id)
    return comment
