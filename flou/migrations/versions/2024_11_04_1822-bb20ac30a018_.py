"""empty message

Revision ID: bb20ac30a018
Revises: 4905fbe6ed41
Create Date: 2024-11-04 18:22:23.261995

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

import flou

# revision identifiers, used by Alembic.
revision: str = 'bb20ac30a018'
down_revision: Union[str, None] = 'f55cc59c874c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.rename_table('ltms', 'ltm_ltms')
    op.rename_table('error', 'engine_error')


def downgrade() -> None:
    op.rename_table('ltm_ltms', 'ltms')
    op.rename_table('engine_error', 'error')
