
from __future__ import annotations

from datetime import datetime
from typing import Any, Literal
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict


JobStatus = Literal["queued", "running", "completed", "failed", "cancelled"]
JobType = Literal["plot_generation", "text_to_image", "image_to_video", "text_to_image_to_video"]


class TextToImageCreate(BaseModel):
    project_id: UUID
    prompt: str = Field(min_length=1)
    negative_prompt: str = ""
    width: int = 512
    height: int = 512
    batch_size: int = 1
    seed: int | None = None
    steps: int = 20
    cfg: float = 8.0
    sampler_name: str = "euler"
    scheduler: str = "simple"
    denoise: float = 1.0
    save_prefix: str = "ComfyUI"


class ImageToVideoCreate(BaseModel):
    project_id: UUID
    source_media_id: UUID
    width: int = 1024
    height: int = 576
    video_frames: int = 14
    motion_bucket_id: int = 127
    fps: int = 6
    augmentation_level: float = 0.0
    add_noise: str = "enable"
    noise_seed: int | None = None
    steps: int = 20
    cfg: float = 8.0
    sampler_name: str = "euler"
    scheduler: str = "simple"
    start_at_step: int = 0
    end_at_step: int = 10000
    return_with_leftover_noise: str = "disable"
    frame_rate: int = 8
    loop_count: int = 0
    format: str = "image/gif"
    pingpong: bool = False
    save_output: bool = True
    save_prefix: str = "AnimateDiff"


class TextToImageToVideoCreate(BaseModel):
    project_id: UUID
    prompt: str = Field(min_length=1)
    negative_prompt: str = ""

    image_width: int = 512
    image_height: int = 512
    image_batch_size: int = 1
    image_seed: int | None = None
    image_steps: int = 20
    image_cfg: float = 8.0
    image_sampler_name: str = "euler"
    image_scheduler: str = "simple"
    image_denoise: float = 1.0

    video_width: int = 1024
    video_height: int = 576
    video_frames: int = 25
    motion_bucket_id: int = 127
    video_fps: int = 10
    augmentation_level: float = 0.0

    video_add_noise: str = "enable"
    video_noise_seed: int | None = None
    video_steps: int = 20
    video_cfg: float = 8.0
    video_sampler_name: str = "euler"
    video_scheduler: str = "simple"
    video_start_at_step: int = 0
    video_end_at_step: int = 10000
    video_return_with_leftover_noise: str = "disable"

    output_frame_rate: int = 8
    output_loop_count: int = 0
    output_format: str = "image/gif"
    output_pingpong: bool = False
    output_save: bool = True
    image_save_prefix: str = "ComfyUI"
    video_save_prefix: str = "AnimateDiff"


class PlotGenerationCreate(BaseModel):
    project_id: UUID
    prompt: str = Field(min_length=1)


class JobUpdate(BaseModel):
    status: JobStatus | None = None
    output_payload: dict[str, Any] | None = None
    error_message: str | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None


class JobProgress(BaseModel):
    stage: str
    percent: int = Field(ge=0, le=100)


class JobRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    user_id: UUID
    project_id: UUID
    job_type: JobType
    status: JobStatus
    input_payload: dict[str, Any] | None = None
    output_payload: dict[str, Any] | None = None
    error_message: str | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class JobOutputItem(BaseModel):
    media_id: UUID
    media_type: str
    content_type: str | None = None
    filename: str
    url: str | None = None
    width: int | None = None
    height: int | None = None
    duration_seconds: int | None = None
    title: str | None = None
    description: str | None = None
    visibility: str | None = None


class JobOutputsRead(BaseModel):
    job_id: UUID
    job_type: JobType
    status: JobStatus
    outputs: list[JobOutputItem]


class JobListResponse(BaseModel):
    items: list[JobRead]
    total: int

