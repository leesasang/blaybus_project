"""add title description visibility to media_meta

Revision ID: b912bed38f68
Revises: 146e2fbcdf32
Create Date: 2026-03-17 13:25:50.950053

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b912bed38f68'
down_revision: Union[str, Sequence[str], None] = '146e2fbcdf32'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('media_meta', sa.Column('title', sa.String(length=255), nullable=True))
    op.add_column('media_meta', sa.Column('description', sa.Text(), nullable=True))
    op.add_column(
        'media_meta',
        sa.Column('visibility', sa.String(length=20), nullable=False, server_default='public')
    )


def downgrade() -> None:
    op.drop_column('media_meta', 'visibility')
    op.drop_column('media_meta', 'description')
    op.drop_column('media_meta', 'title')
