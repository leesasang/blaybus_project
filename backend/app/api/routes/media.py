from __future__ import annotations

from pathlib import Path
from uuid import UUID

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.crud.media import (
    create_media,
    get_media_list_by_project,
    get_media_stats,
    increment_media_view_count,
    update_media,
)
from app.db.database import get_db
from app.db.models import MediaAsset, Project, User
from app.schemas.media import (
    MediaCreate,
    MediaDetailResponse,
    MediaListResponse,
    MediaResponse,
    MediaUpdate,
)
from app.services.storage.factory import get_storage_service
from app.utils.storage import build_storage_path

router = APIRouter(prefix="/media", tags=["media"])


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


def require_media_owner(db: Session, media_id: UUID, current_user: User) -> MediaAsset:
    media = db.query(MediaAsset).filter(MediaAsset.id == media_id).first()
    if media is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Media not found",
        )

    if media.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions",
        )

    return media


@router.post("", response_model=MediaResponse, status_code=status.HTTP_201_CREATED)
def create_media_endpoint(
    payload: MediaCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> MediaResponse:
    require_project_owner(db, payload.project_id, current_user)

    media = create_media(
        db=db,
        media_in=payload,
        user_id=current_user.id,
    )
    return media

@router.post("/upload", response_model=MediaResponse, status_code=status.HTTP_201_CREATED)
async def upload_media_endpoint(
    project_id: UUID = Form(...),
    title: str = Form(...),
    description: str = Form(""),
    visibility: str = Form("private"),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> MediaResponse:
    require_project_owner(db, project_id, current_user)

    data = await file.read()

    if not data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Empty file",
        )

    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only image uploads are allowed",
        )

    relative_path = build_storage_path(
        project_id=str(project_id),
        original_filename=file.filename or "upload.bin",
        media_dir="images",
    )

    storage = get_storage_service()

    try:
        saved = storage.save_file(
            data=data,
            relative_path=relative_path,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"R2 upload failed: {exc}",
        ) from exc

    filename = Path(relative_path).name

    payload = MediaCreate(
        project_id=project_id,
        media_type="image",
        origin_type="upload",
        filename=filename,
        original_filename=file.filename,
        content_type=saved["content_type"],
        size_bytes=saved["size_bytes"],
        storage_provider=saved["storage_provider"],
        storage_path=saved["storage_path"],
        public_url=saved["public_url"],
        status="ready",
        title=title,
        description=description,
        visibility=visibility,
    )

    try:
        media = create_media(
            db=db,
            media_in=payload,
            user_id=current_user.id,
        )
    except Exception as exc:
        try:
            if hasattr(storage, "delete_file"):
                storage.delete_file(relative_path=relative_path)
        except Exception:
            pass

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"DB save failed after upload: {exc}",
        ) from exc

    return media

@router.get("/{media_id}", response_model=MediaDetailResponse)
def get_media_endpoint(
    media_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> MediaDetailResponse:
    media = require_media_owner(db, media_id, current_user)

    increment_media_view_count(db=db, media_asset_id=media_id)
    stats = get_media_stats(db=db, media_asset_id=media_id)

    data = MediaResponse.model_validate(media, from_attributes=True).model_dump()
    return MediaDetailResponse(**data, stats=stats)


@router.patch("/{media_id}", response_model=MediaResponse)
def update_media_endpoint(
    media_id: UUID,
    payload: MediaUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> MediaResponse:
    media = require_media_owner(db, media_id, current_user)

    updated = update_media(db=db, media=media, media_in=payload)
    return updated


@router.get("/project/{project_id}", response_model=MediaListResponse)
def list_project_media_endpoint(
    project_id: UUID,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> MediaListResponse:
    require_project_owner(db, project_id, current_user)

    items, total = get_media_list_by_project(
        db=db,
        project_id=project_id,
        skip=skip,
        limit=limit,
    )
    return MediaListResponse(items=items, total=total)
