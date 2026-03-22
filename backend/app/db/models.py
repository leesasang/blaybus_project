from sqlalchemy import Column, String, Text, Integer, TIMESTAMP, ForeignKey, BigInteger, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
import uuid

from app.db.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), nullable=False, unique=True)
    nickname = Column(String(100), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    projects = relationship("Project", back_populates="user", cascade="all, delete-orphan")
    jobs = relationship("Job", back_populates="user", cascade="all, delete-orphan")
    media_assets = relationship("MediaAsset", back_populates="user", cascade="all, delete-orphan")
    likes = relationship("Like", back_populates="user", cascade="all, delete-orphan")
    bookmarks = relationship("Bookmark", back_populates="user", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="user", cascade="all, delete-orphan")
    creator_profile = relationship("CreatorProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")


class Project(Base):
    __tablename__ = "projects"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    title = Column(String(255), nullable=True)
    prompt = Column(Text, nullable=False)
    plot_text = Column(Text, nullable=True)
    status = Column(String(50), nullable=False, default="pending")
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="projects")
    jobs = relationship("Job", back_populates="project", cascade="all, delete-orphan")
    media_assets = relationship("MediaAsset", back_populates="project", cascade="all, delete-orphan")


class Job(Base):
    __tablename__ = "jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    job_type = Column(String(50), nullable=False)
    status = Column(String(50), nullable=False, default="queued")
    input_payload = Column(JSONB, nullable=True)
    output_payload = Column(JSONB, nullable=True)
    error_message = Column(Text, nullable=True)
    started_at = Column(TIMESTAMP, nullable=True)
    completed_at = Column(TIMESTAMP, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="jobs")
    project = relationship("Project", back_populates="jobs")
    media_assets = relationship("MediaAsset", back_populates="job")


class MediaAsset(Base):
    __tablename__ = "media_meta"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    project_id = Column(UUID(as_uuid=True), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id", ondelete="SET NULL"), nullable=True)

    media_type = Column(String(30), nullable=False)
    origin_type = Column(String(30), nullable=False)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=True)
    content_type = Column(String(100), nullable=False)
    size_bytes = Column(BigInteger, nullable=True)

    storage_provider = Column(String(30), nullable=False, default="firebase")
    storage_path = Column(Text, nullable=False)
    public_url = Column(Text, nullable=True)
    thumbnail_url = Column(Text, nullable=True)

    status = Column(String(50), nullable=False, default="pending_upload")
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    duration_seconds = Column(Integer, nullable=True)

    prompt_text = Column(Text, nullable=True)
    title = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    visibility = Column(String(20), nullable=False, default="public")
    error_message = Column(Text, nullable=True)

    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    deleted_at = Column(TIMESTAMP, nullable=True)

    user = relationship("User", back_populates="media_assets")
    project = relationship("Project", back_populates="media_assets")
    job = relationship("Job", back_populates="media_assets")

    likes = relationship("Like", back_populates="media_asset", cascade="all, delete-orphan")
    bookmarks = relationship("Bookmark", back_populates="media_asset", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="media_asset", cascade="all, delete-orphan")
    stats = relationship("MediaStat", back_populates="media_asset", uselist=False, cascade="all, delete-orphan")


class Like(Base):
    __tablename__ = "likes"
    __table_args__ = (
        UniqueConstraint("user_id", "media_asset_id", name="uq_likes_user_media"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    media_asset_id = Column(UUID(as_uuid=True), ForeignKey("media_meta.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

    user = relationship("User", back_populates="likes")
    media_asset = relationship("MediaAsset", back_populates="likes")


class Bookmark(Base):
    __tablename__ = "bookmarks"
    __table_args__ = (
        UniqueConstraint("user_id", "media_asset_id", name="uq_bookmarks_user_media"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    media_asset_id = Column(UUID(as_uuid=True), ForeignKey("media_meta.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())

    user = relationship("User", back_populates="bookmarks")
    media_asset = relationship("MediaAsset", back_populates="bookmarks")


class Comment(Base):
    __tablename__ = "comments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    media_asset_id = Column(UUID(as_uuid=True), ForeignKey("media_meta.id", ondelete="CASCADE"), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    deleted_at = Column(TIMESTAMP, nullable=True)

    user = relationship("User", back_populates="comments")
    media_asset = relationship("MediaAsset", back_populates="comments")


class MediaStat(Base):
    __tablename__ = "media_stats"

    media_asset_id = Column(UUID(as_uuid=True), ForeignKey("media_meta.id", ondelete="CASCADE"), primary_key=True)
    view_count = Column(BigInteger, nullable=False, default=0)
    like_count = Column(BigInteger, nullable=False, default=0)
    comment_count = Column(BigInteger, nullable=False, default=0)
    bookmark_count = Column(BigInteger, nullable=False, default=0)
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    media_asset = relationship("MediaAsset", back_populates="stats")


class CreatorProfile(Base):
    __tablename__ = "creator_profiles"

    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    creator_score = Column(BigInteger, nullable=False, default=0)
    creator_level = Column(Integer, nullable=False, default=1)
    unlocked_features = Column(JSONB, nullable=True)
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    user = relationship("User", back_populates="creator_profile")
