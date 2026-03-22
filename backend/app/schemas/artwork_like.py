from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ArtworkLikeCreate(BaseModel):
    media_asset_id: UUID


class ArtworkLikeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    media_asset_id: UUID
    created_at: datetime


class ArtworkLikeCountResponse(BaseModel):
    media_asset_id: UUID
    like_count: int
