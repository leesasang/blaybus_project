from __future__ import annotations

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.db.models import Project
from app.schemas.project import ProjectCreate


def create_project(db: Session, project_in: ProjectCreate, user_id):
    project = Project(
        user_id=user_id,
        prompt=project_in.prompt,
        plot_text=project_in.plot_text,
        status="pending",
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return project


def get_projects_by_user(db: Session, user_id):
    return (
        db.query(Project)
        .filter(Project.user_id == user_id)
        .order_by(Project.created_at.desc())
        .all()
    )


def get_project_by_id(db: Session, project_id: UUID) -> Project | None:
    stmt = select(Project).where(Project.id == project_id)
    return db.scalar(stmt)
