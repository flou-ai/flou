"""rename_state_to_store

Revision ID: 1354cd2bcfec
Revises: b32a36208b6c
Create Date: 2025-03-20 17:10:18.593023

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
from flou.database.utils import JSONType

# revision identifiers, used by Alembic.
revision: str = '1354cd2bcfec'
down_revision: Union[str, None] = 'b32a36208b6c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add new store column
    op.add_column('ltm_ltms', sa.Column('store', JSONType(), nullable=False, server_default='{}'))
    
    # Copy data from state to store
    op.execute(
        """
        UPDATE ltm_ltms 
        SET store = state
        """
    )
    
    # Drop old state column
    op.drop_column('ltm_ltms', 'state')


def downgrade() -> None:
    # No downgrade available - pre 1.0 breaking change
    raise NotImplementedError("Downgrade not supported for this migration")
