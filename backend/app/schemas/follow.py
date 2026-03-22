from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class FollowActionResponse(BaseModel):
    message: str
    target_user_id: UUID


class FollowStatusResponse(BaseModel):
    user_id: UUID
    target_user_id: UUID
    is_following: bool


class FollowUserItem(BaseModel):
    user_id: UUID
    nickname: str
    followed_at: datetime | None = None


class FollowListResponse(BaseModel):
    count: int
    users: list[FollowUserItem]
