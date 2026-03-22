from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.crud.follow import (
    create_follow,
    get_follow_relation,
    get_user_by_id,
    is_following,
    list_followers,
    list_following,
    remove_follow,
)
from app.db.database import get_db
from app.db.models import User
from app.schemas.follow import (
    FollowActionResponse,
    FollowListResponse,
    FollowStatusResponse,
)

router = APIRouter(prefix="/users", tags=["follow"])


@router.post("/{target_user_id}/follow", response_model=FollowActionResponse)
def follow_user(
    target_user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.id == target_user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot follow yourself.",
        )

    target_user = get_user_by_id(db, target_user_id)
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Target user not found.",
        )

    existing = get_follow_relation(db, current_user.id, target_user_id)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Already following this user.",
        )

    create_follow(db, current_user.id, target_user_id)

    return FollowActionResponse(
        message="Followed successfully.",
        target_user_id=target_user_id,
    )


@router.delete("/{target_user_id}/follow", response_model=FollowActionResponse)
def unfollow_user(
    target_user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if current_user.id == target_user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot unfollow yourself.",
        )

    target_user = get_user_by_id(db, target_user_id)
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Target user not found.",
        )

    removed = remove_follow(db, current_user.id, target_user_id)
    if not removed:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Follow relationship not found.",
        )

    return FollowActionResponse(
        message="Unfollowed successfully.",
        target_user_id=target_user_id,
    )


@router.get("/{user_id}/followers", response_model=FollowListResponse)
def get_followers(
    user_id: UUID,
    db: Session = Depends(get_db),
):
    target_user = get_user_by_id(db, user_id)
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )

    users = list_followers(db, user_id)
    return FollowListResponse(count=len(users), users=users)


@router.get("/{user_id}/following", response_model=FollowListResponse)
def get_following(
    user_id: UUID,
    db: Session = Depends(get_db),
):
    target_user = get_user_by_id(db, user_id)
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found.",
        )

    users = list_following(db, user_id)
    return FollowListResponse(count=len(users), users=users)


@router.get("/{target_user_id}/follow-status", response_model=FollowStatusResponse)
def get_follow_status(
    target_user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    target_user = get_user_by_id(db, target_user_id)
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Target user not found.",
        )

    return FollowStatusResponse(
        user_id=current_user.id,
        target_user_id=target_user_id,
        is_following=is_following(db, current_user.id, target_user_id),
    )
