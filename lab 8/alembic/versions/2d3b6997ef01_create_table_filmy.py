"""create table filmy

Revision ID: 2d3b6997ef01
Revises: 97b2a690258a
Create Date: 2025-12-02 18:32:08.475394

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2d3b6997ef01'
down_revision: Union[str, Sequence[str], None] = '97b2a690258a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
