from uuid import UUID

from sqlalchemy.orm import Session

from app.core.security import hash_password
from app.db.models import User
from app.schemas.user import UserCreate


def create_user(db: Session, user_in: UserCreate) -> User:
    user = User(
        email=user_in.email,
        nickname=user_in.nickname,
        hashed_password=hash_password(user_in.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_users(db: Session):
    return db.query(User).order_by(User.created_at.desc()).all()


def get_user_by_email(db: Session, email: str):
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(db: Session, user_id: str):
    try:
        uid = UUID(str(user_id))
    except (ValueError, TypeError):
        return None
    return db.query(User).filter(User.id == uid).first()
