from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class MediaStatsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    media_asset_id: UUID
    view_count: int
    like_count: int
    comment_count: int
    bookmark_count: int
    updated_at: datetime


class MediaCreate(BaseModel):
    project_id: UUID
    job_id: Optional[UUID] = None

    media_type: str = Field(..., max_length=30)
    origin_type: str = Field(..., max_length=30)

    filename: str = Field(..., max_length=255)
    original_filename: Optional[str] = Field(default=None, max_length=255)
    content_type: str = Field(..., max_length=100)
    size_bytes: Optional[int] = None

    storage_provider: str = Field(default="firebase", max_length=30)
    storage_path: str
    public_url: Optional[str] = None
    thumbnail_url: Optional[str] = None

    status: str = Field(default="pending_upload", max_length=50)
    width: Optional[int] = None
    height: Optional[int] = None
    duration_seconds: Optional[int] = None

    prompt_text: Optional[str] = None
    title: Optional[str] = Field(default=None, max_length=255)
    description: Optional[str] = None
    visibility: str = Field(default="public", max_length=20)
    error_message: Optional[str] = None


class MediaUpdate(BaseModel):
    job_id: Optional[UUID] = None

    original_filename: Optional[str] = Field(default=None, max_length=255)
    size_bytes: Optional[int] = None

    public_url: Optional[str] = None
    thumbnail_url: Optional[str] = None

    status: Optional[str] = Field(default=None, max_length=50)
    width: Optional[int] = None
    height: Optional[int] = None
    duration_seconds: Optional[int] = None

    prompt_text: Optional[str] = None
    title: Optional[str] = Field(default=None, max_length=255)
    description: Optional[str] = None
    visibility: Optional[str] = Field(default=None, max_length=20)
    error_message: Optional[str] = None


class MediaResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    project_id: UUID
    job_id: Optional[UUID]

    media_type: str
    origin_type: str

    filename: str
    original_filename: Optional[str]
    content_type: str
    size_bytes: Optional[int]

    storage_provider: str
    storage_path: str
    public_url: Optional[str]
    thumbnail_url: Optional[str]

    status: str
    width: Optional[int]
    height: Optional[int]
    duration_seconds: Optional[int]

    prompt_text: Optional[str]
    title: Optional[str]
    description: Optional[str]
    visibility: str
    error_message: Optional[str]

    created_at: datetime
    updated_at: datetime
    deleted_at: Optional[datetime]


class MediaDetailResponse(MediaResponse):
    stats: Optional[MediaStatsResponse] = None


class MediaListResponse(BaseModel):
    items: list[MediaResponse]
    total: int
