
from __future__ import annotations

from datetime import datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.crud.image_job import (
    create_job,
    get_jobs_by_project,
    update_job,
)
from app.db.database import get_db
from app.db.models import Job, MediaAsset, Project, User
from app.services.media_from_job import create_media_from_job_result
from app.services.job_runner import schedule_job_processing
from app.schemas.image_job import (
    ImageToVideoCreate,
    JobListResponse,
    JobOutputsRead,
    JobOutputItem,
    JobRead,
    JobUpdate,
    PlotGenerationCreate,
    TextToImageCreate,
    TextToImageToVideoCreate,
)

router = APIRouter(prefix="/api/v1/jobs", tags=["jobs"])


def require_project_owner(db: Session, project_id: UUID, current_user: User) -> Project:
    project = db.query(Project).filter(Project.id == project_id).first()

    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    if project.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )

    return project


def require_job_owner(db: Session, job_id: UUID, current_user: User) -> Job:
    job = db.query(Job).filter(Job.id == job_id).first()

    if job is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job not found",
        )

    if job.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )

    return job


def require_source_media_owner(db: Session, media_id: UUID, current_user: User) -> MediaAsset:
    media = db.query(MediaAsset).filter(MediaAsset.id == media_id).first()

    if media is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Source media not found",
        )

    if media.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )

    return media


@router.post("/text-to-image", response_model=JobRead, status_code=status.HTTP_201_CREATED)
def create_text_to_image_job_endpoint(
    payload: TextToImageCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> JobRead:
    require_project_owner(db, payload.project_id, current_user)

    job = create_job(
        db=db,
        user_id=current_user.id,
        project_id=payload.project_id,
        job_type="text_to_image",
        input_payload=payload.model_dump(mode="json"),
    )
    schedule_job_processing(job.id)

    return job


@router.post("/image-to-video", response_model=JobRead, status_code=status.HTTP_201_CREATED)
def create_image_to_video_job_endpoint(
    payload: ImageToVideoCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> JobRead:
    require_project_owner(db, payload.project_id, current_user)
    source_media = require_source_media_owner(db, payload.source_media_id, current_user)

    if source_media.media_type != "image":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="source_media_id must reference image media",
        )

    job = create_job(
        db=db,
        user_id=current_user.id,
        project_id=payload.project_id,
        job_type="image_to_video",
        input_payload=payload.model_dump(mode="json"),
    )
    schedule_job_processing(job.id)

    return job


@router.post("/text-to-image-to-video", response_model=JobRead, status_code=status.HTTP_201_CREATED)
def create_text_to_image_to_video_job_endpoint(
    payload: TextToImageToVideoCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> JobRead:
    require_project_owner(db, payload.project_id, current_user)

    job = create_job(
        db=db,
        user_id=current_user.id,
        project_id=payload.project_id,
        job_type="text_to_image_to_video",
        input_payload=payload.model_dump(mode="json"),
    )
    schedule_job_processing(job.id)

    return job


@router.post("/plot-generation", response_model=JobRead, status_code=status.HTTP_201_CREATED)
def create_plot_generation_job_endpoint(
    payload: PlotGenerationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> JobRead:
    require_project_owner(db, payload.project_id, current_user)

    job = create_job(
        db=db,
        user_id=current_user.id,
        project_id=payload.project_id,
        job_type="plot_generation",
        input_payload=payload.model_dump(mode="json"),
    )
    schedule_job_processing(job.id)

    return job


@router.get("/{job_id}", response_model=JobRead)
def get_job_endpoint(
    job_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> JobRead:
    job = require_job_owner(db, job_id, current_user)
    return job


@router.get("/project/{project_id}", response_model=JobListResponse)
def list_project_jobs_endpoint(
    project_id: UUID,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> JobListResponse:
    require_project_owner(db, project_id, current_user)

    items, total = get_jobs_by_project(
        db=db,
        project_id=project_id,
        skip=skip,
        limit=limit,
    )

    return JobListResponse(items=items, total=total)


@router.get("/{job_id}/outputs", response_model=JobOutputsRead)
def get_job_outputs_endpoint(
    job_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> JobOutputsRead:
    job = require_job_owner(db, job_id, current_user)

    assets = (
        db.query(MediaAsset)
        .filter(MediaAsset.job_id == job.id, MediaAsset.user_id == current_user.id)
        .order_by(MediaAsset.created_at.asc())
        .all()
    )

    outputs = [
        JobOutputItem(
            media_id=asset.id,
            media_type=asset.media_type,
            content_type=asset.content_type,
            filename=asset.filename,
            url=asset.public_url,
            width=asset.width,
            height=asset.height,
            duration_seconds=asset.duration_seconds,
            title=asset.title,
            description=asset.description,
            visibility=asset.visibility,
        )
        for asset in assets
    ]

    return JobOutputsRead(
        job_id=job.id,
        job_type=job.job_type,
        status=job.status,
        outputs=outputs,
    )


@router.patch("/{job_id}", response_model=JobRead)
def patch_job_endpoint(
    job_id: UUID,
    payload: JobUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> JobRead:
    job = require_job_owner(db, job_id, current_user)

    update_data = payload.model_dump(exclude_unset=True)
    new_status = update_data.get("status")

    if new_status is not None:
        allowed_statuses = {"queued", "running", "completed", "failed", "cancelled"}

        if new_status not in allowed_statuses:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid status",
            )

        output_payload = update_data.get("output_payload", job.output_payload) or {}
        progress = output_payload.get("progress", {})

        if new_status == "queued":
            progress["stage"] = "queued"
            progress["percent"] = 0

        if new_status == "running":
            progress["stage"] = progress.get("stage", "running")
            progress["percent"] = progress.get("percent", 50)
            if "started_at" not in update_data:
                update_data["started_at"] = datetime.now(timezone.utc)

        if new_status in {"completed", "failed", "cancelled"}:
            progress["stage"] = "completed" if new_status == "completed" else new_status
            progress["percent"] = 100
            if "completed_at" not in update_data:
                update_data["completed_at"] = datetime.now(timezone.utc)

        output_payload["progress"] = progress
        update_data["output_payload"] = output_payload

    if new_status == "completed":
        output_payload = update_data.get("output_payload", job.output_payload) or {}

        if job.job_type in {"text_to_image", "image_to_video", "text_to_image_to_video"}:
            outputs = output_payload.get("outputs")
            if not isinstance(outputs, list) or len(outputs) == 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="output_payload.outputs is required when generation job is completed",
                )

            for item in outputs:
                if not item.get("filename"):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Each output item must include filename",
                    )
                if not item.get("storage_path"):
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Each output item must include storage_path",
                    )

        if job.job_type == "plot_generation":
            plot_text = output_payload.get("plot_text")
            if plot_text:
                project = db.query(Project).filter(Project.id == job.project_id).first()
                if project:
                    project.plot_text = plot_text
                    db.add(project)
                    db.commit()

    try:
        updated_job = update_job(
            db=db,
            db_job=job,
            update_data=update_data,
        )

        if updated_job.status == "completed":
            create_media_from_job_result(db=db, job=updated_job)

        return updated_job

    except ValueError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc

    except Exception:
        db.rollback()
        raise
