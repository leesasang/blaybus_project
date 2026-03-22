
from __future__ import annotations

from typing import Any
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.db.models import Job


def create_job(
    db: Session,
    *,
    user_id: UUID,
    project_id: UUID,
    job_type: str,
    input_payload: dict[str, Any],
) -> Job:
    job = Job(
        user_id=user_id,
        project_id=project_id,
        job_type=job_type,
        status="queued",
        input_payload=input_payload,
        output_payload={
            "progress": {
                "stage": "queued",
                "percent": 0,
            }
        },
    )
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


def get_job_by_id(db: Session, *, job_id: UUID) -> Job | None:
    stmt = select(Job).where(Job.id == job_id)
    return db.scalar(stmt)


def get_jobs_by_project(
    db: Session,
    *,
    project_id: UUID,
    skip: int = 0,
    limit: int = 20,
) -> tuple[list[Job], int]:
    conditions = [Job.project_id == project_id]

    total_stmt = select(func.count()).select_from(Job).where(*conditions)
    total = db.scalar(total_stmt) or 0

    stmt = (
        select(Job)
        .where(*conditions)
        .order_by(Job.created_at.desc())
        .offset(skip)
        .limit(limit)
    )
    items = list(db.scalars(stmt).all())

    return items, total


def update_job(
    db: Session,
    *,
    db_job: Job,
    update_data: dict[str, Any],
) -> Job:
    for field, value in update_data.items():
        setattr(db_job, field, value)

    db.add(db_job)
    db.commit()
    db.refresh(db_job)
    return db_job
