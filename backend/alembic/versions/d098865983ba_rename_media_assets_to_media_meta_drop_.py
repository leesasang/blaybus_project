"""rename media_assets to media_meta drop jobs add user_follows

Revision ID: d098865983ba
Revises: faf642b95ef2
Create Date: 2026-03-15 11:43:22.752489

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd098865983ba'
down_revision: Union[str, Sequence[str], None] = 'faf642b95ef2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
