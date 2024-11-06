"""empty message

Revision ID: 076b9aea5f59
Revises: 69c9354bb7ff
Create Date: 2024-11-06 14:32:55.161297

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '076b9aea5f59'
down_revision: Union[str, None] = '69c9354bb7ff'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('experiments_experiments', 'id', server_default=sa.text('gen_random_uuid()'))
    op.alter_column('experiments_trials', 'id', server_default=sa.text('gen_random_uuid()'))


def downgrade() -> None:
    op.alter_column('experiments_experiments', 'id', server_default=None)
    op.alter_column('experiments_trials', 'id', server_default=None)
