"""add jobs table and media_meta job_id

Revision ID: 146e2fbcdf32
Revises: d098865983ba
Create Date: 2026-03-16

faf642에서 이미 jobs·media_assets(job_id 포함)가 생성될 수 있어 idempotent 하게 처리합니다.

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect
from sqlalchemy.dialects import postgresql


revision: str = "146e2fbcdf32"
down_revision: Union[str, Sequence[str], None] = "d098865983ba"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    bind = op.get_bind()
    insp = inspect(bind)
    tables = set(insp.get_table_names())

    if "jobs" not in tables:
        op.create_table(
            "jobs",
            sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("user_id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("project_id", postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column("job_type", sa.String(length=50), nullable=False),
            sa.Column("status", sa.String(length=50), nullable=False, server_default="queued"),
            sa.Column("input_payload", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
            sa.Column("output_payload", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
            sa.Column("error_message", sa.Text(), nullable=True),
            sa.Column("started_at", sa.TIMESTAMP(), nullable=True),
            sa.Column("completed_at", sa.TIMESTAMP(), nullable=True),
            sa.Column("created_at", sa.TIMESTAMP(), server_default=sa.text("now()"), nullable=True),
            sa.Column("updated_at", sa.TIMESTAMP(), server_default=sa.text("now()"), nullable=True),
            sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
            sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
            sa.PrimaryKeyConstraint("id"),
        )

    if "media_assets" in tables and "media_meta" not in tables:
        op.rename_table("media_assets", "media_meta")

    insp = inspect(bind)
    if "media_meta" not in insp.get_table_names():
        return

    cols = {c["name"] for c in insp.get_columns("media_meta")}
    if "job_id" in cols:
        return

    op.add_column(
        "media_meta",
        sa.Column("job_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_foreign_key(
        "media_meta_job_id_fkey",
        "media_meta",
        "jobs",
        ["job_id"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    bind = op.get_bind()
    insp = inspect(bind)
    tables = set(insp.get_table_names())

    if "media_meta" in tables:
        fks = insp.get_foreign_keys("media_meta")
        for fk in fks:
            if fk.get("name") == "media_meta_job_id_fkey":
                op.drop_constraint("media_meta_job_id_fkey", "media_meta", type_="foreignkey")
                break
        cols = {c["name"] for c in insp.get_columns("media_meta")}
        if "job_id" in cols:
            op.drop_column("media_meta", "job_id")

    if "media_assets" not in tables and "media_meta" in tables:
        op.rename_table("media_meta", "media_assets")

    if "jobs" in tables:
        op.drop_table("jobs")
