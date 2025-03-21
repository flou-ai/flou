"""rename_schema_to_json_schema

Revision ID: f744a9c8282e
Revises: 8542e7779a73
Create Date: 2025-01-16 17:57:17.378577

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f744a9c8282e'
down_revision: Union[str, None] = '8542e7779a73'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
