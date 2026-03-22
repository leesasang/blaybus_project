from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CommentCreate(BaseModel):
    media_asset_id: UUID
    content: str = Field(..., min_length=1)


class CommentUpdate(BaseModel):
    content: str = Field(..., min_length=1)


class CommentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    media_asset_id: UUID
    content: str
    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime]


class CommentListResponse(BaseModel):
    items: list[CommentResponse]
    total: int
