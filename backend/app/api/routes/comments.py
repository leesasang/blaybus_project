from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.crud.comment import (
    create_comment,
    get_comment_by_id,
    get_comments_by_media,
    soft_delete_comment,
    update_comment,
)
from app.crud.media import get_media_by_id
from app.db.database import get_db
from app.db.models import User
from app.schemas.comment import (
    CommentCreate,
    CommentListResponse,
    CommentResponse,
    CommentUpdate,
)

router = APIRouter(prefix="/comments", tags=["comments"])


@router.post("", response_model=CommentResponse, status_code=status.HTTP_201_CREATED)
def create_comment_endpoint(
    payload: CommentCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CommentResponse:
    media = get_media_by_id(db=db, media_id=payload.media_asset_id)
    if media is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Media not found",
        )

    comment = create_comment(
        db=db,
        user_id=current_user.id,
        media_asset_id=payload.media_asset_id,
        content=payload.content,
    )
    return comment


@router.get("/media/{media_asset_id}", response_model=CommentListResponse)
def list_comments_endpoint(
    media_asset_id: UUID,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> CommentListResponse:
    media = get_media_by_id(db=db, media_id=media_asset_id)
    if media is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Media not found",
        )

    items, total = get_comments_by_media(
        db=db,
        media_asset_id=media_asset_id,
        skip=skip,
        limit=limit,
    )
    return CommentListResponse(items=items, total=total)


@router.patch("/{comment_id}", response_model=CommentResponse)
def update_comment_endpoint(
    comment_id: UUID,
    payload: CommentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CommentResponse:
    comment = get_comment_by_id(db=db, comment_id=comment_id)
    if comment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found",
        )

    if comment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only edit your own comment",
        )

    updated = update_comment(db=db, comment=comment, comment_in=payload)
    return updated


@router.delete("/{comment_id}", response_model=CommentResponse)
def delete_comment_endpoint(
    comment_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> CommentResponse:
    comment = get_comment_by_id(db=db, comment_id=comment_id)
    if comment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found",
        )

    if comment.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own comment",
        )

    deleted = soft_delete_comment(db=db, comment=comment)
    return deleted
