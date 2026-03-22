from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime


class ProjectCreate(BaseModel):
    prompt: str
    plot_text: Optional[str] = None


class ProjectRead(BaseModel):
    id: UUID
    user_id: UUID
    prompt: str
    plot_text: Optional[str]
    status: str
    created_at: datetime

    class Config:
        from_attributes = True
