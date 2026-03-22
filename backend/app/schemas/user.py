from pydantic import BaseModel, EmailStr
from uuid import UUID
from datetime import datetime


class UserCreate(BaseModel):
    email: EmailStr
    nickname: str
    password: str


class UserRead(BaseModel):
    id: UUID
    email: EmailStr
    nickname: str
    created_at: datetime

    class Config:
        from_attributes = True
