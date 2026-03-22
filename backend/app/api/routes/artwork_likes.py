from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.crud.artwork_like import create_like, delete_like, get_like_count
from app.crud.media import get_media_by_id
from app.db.database import get_db
from app.db.models import User
from app.schemas.artwork_like import (
    ArtworkLikeCreate,
    ArtworkLikeCountResponse,
    ArtworkLikeResponse,
)

router = APIRouter(prefix="/artwork-likes", tags=["artwork-likes"])


@router.post("", response_model=ArtworkLikeResponse, status_code=status.HTTP_201_CREATED)
def create_like_endpoint(
    payload: ArtworkLikeCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> ArtworkLikeResponse:
    media = get_media_by_id(db=db, media_id=payload.media_asset_id)
    if media is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Media not found",
        )

    like = create_like(
        db=db,
        user_id=current_user.id,
        media_asset_id=payload.media_asset_id,
    )
    return like


@router.delete("/{media_asset_id}", status_code=status.HTTP_200_OK)
def delete_like_endpoint(
    media_asset_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict:
    deleted = delete_like(
        db=db,
        user_id=current_user.id,
        media_asset_id=media_asset_id,
    )
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Like not found",
        )
    return {"message": "Like removed"}


@router.get("/count/{media_asset_id}", response_model=ArtworkLikeCountResponse)
def get_like_count_endpoint(
    media_asset_id: UUID,
    db: Session = Depends(get_db),
) -> ArtworkLikeCountResponse:
    media = get_media_by_id(db=db, media_id=media_asset_id)
    if media is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Media not found",
        )

    like_count = get_like_count(db=db, media_asset_id=media_asset_id)
    return ArtworkLikeCountResponse(
        media_asset_id=media_asset_id,
        like_count=like_count,
    )
