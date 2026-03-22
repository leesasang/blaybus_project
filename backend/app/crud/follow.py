from __future__ import annotations

from uuid import UUID

from sqlalchemy.orm import Session

from app.models.follow import UserFollow
from app.db.models import User


def get_user_by_id(db: Session, user_id: UUID) -> User | None:
    return db.query(User).filter(User.id == user_id).first()


def get_follow_relation(db: Session, follower_id: UUID, following_id: UUID) -> UserFollow | None:
    return (
        db.query(UserFollow)
        .filter(
            UserFollow.follower_id == follower_id,
            UserFollow.following_id == following_id,
        )
        .first()
    )


def create_follow(db: Session, follower_id: UUID, following_id: UUID) -> UserFollow:
    follow = UserFollow(
        follower_id=follower_id,
        following_id=following_id,
    )
    db.add(follow)
    db.commit()
    db.refresh(follow)
    return follow


def remove_follow(db: Session, follower_id: UUID, following_id: UUID) -> bool:
    follow = get_follow_relation(db, follower_id, following_id)
    if not follow:
        return False

    db.delete(follow)
    db.commit()
    return True


def is_following(db: Session, follower_id: UUID, following_id: UUID) -> bool:
    return get_follow_relation(db, follower_id, following_id) is not None


def list_followers(db: Session, user_id: UUID) -> list[dict]:
    rows = (
        db.query(UserFollow, User)
        .join(User, UserFollow.follower_id == User.id)
        .filter(UserFollow.following_id == user_id)
        .order_by(UserFollow.created_at.desc())
        .all()
    )

    result = []
    for follow, user in rows:
        result.append(
            {
                "user_id": user.id,
                "nickname": user.nickname,
                "followed_at": follow.created_at,
            }
        )
    return result


def list_following(db: Session, user_id: UUID) -> list[dict]:
    rows = (
        db.query(UserFollow, User)
        .join(User, UserFollow.following_id == User.id)
        .filter(UserFollow.follower_id == user_id)
        .order_by(UserFollow.created_at.desc())
        .all()
    )

    result = []
    for follow, user in rows:
        result.append(
            {
                "user_id": user.id,
                "nickname": user.nickname,
                "followed_at": follow.created_at,
            }
        )
    return result
