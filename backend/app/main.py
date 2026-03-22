from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.routes.users import router as users_router
from app.api.routes.projects import router as projects_router
from app.api.routes.auth import router as auth_router
from app.api.routes.media import router as media_router
from app.api.routes.follow import router as follow_router
from app.api.routes.image_jobs import router as image_jobs_router
from app.api.routes.artworks import router as artworks_router
from app.api.routes.comments import router as comments_router
from app.api.routes.artwork_likes import router as artwork_likes_router

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "http://localhost:8080",
        "http://127.0.0.1:8080",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/storage", StaticFiles(directory="storage"), name="storage")

app.include_router(users_router)
app.include_router(projects_router)
app.include_router(auth_router)
app.include_router(media_router)
app.include_router(follow_router)
app.include_router(image_jobs_router)
app.include_router(artworks_router)
app.include_router(comments_router)
app.include_router(artwork_likes_router)


@app.get("/")
def read_root():
    return {"message": "FastAPI + PostgreSQL connection success"}
