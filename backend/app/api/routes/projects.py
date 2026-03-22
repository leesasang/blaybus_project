from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.api.deps import get_current_user
from app.schemas.project import ProjectCreate, ProjectRead
from app.crud.project import create_project, get_projects_by_user

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("/", response_model=ProjectRead)
def create_project_api(
    project_in: ProjectCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return create_project(db, project_in, current_user.id)


@router.get("/", response_model=list[ProjectRead])
def list_projects_api(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return get_projects_by_user(db, current_user.id)
