"""empty message

Revision ID: 69c9354bb7ff
Revises: d17bb320f4d3
Create Date: 2024-11-06 14:30:21.018516

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '69c9354bb7ff'
down_revision: Union[str, None] = 'd17bb320f4d3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('experiments_experiments_ltm_id_fkey', 'experiments_experiments', type_='foreignkey')
    op.drop_column('experiments_experiments', 'rollback_index')
    op.drop_column('experiments_experiments', 'ltm_id')
    op.drop_column('experiments_experiments', 'snapshot_index')
    op.add_column('experiments_trials', sa.Column('ltm_id', sa.Integer(), nullable=False))
    op.create_foreign_key(None, 'experiments_trials', 'ltm_ltms', ['ltm_id'], ['id'])
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'experiments_trials', type_='foreignkey')
    op.drop_column('experiments_trials', 'ltm_id')
    op.add_column('experiments_experiments', sa.Column('snapshot_index', sa.INTEGER(), autoincrement=False, nullable=False))
    op.add_column('experiments_experiments', sa.Column('ltm_id', sa.INTEGER(), autoincrement=False, nullable=False))
    op.add_column('experiments_experiments', sa.Column('rollback_index', sa.INTEGER(), autoincrement=False, nullable=False))
    op.create_foreign_key('experiments_experiments_ltm_id_fkey', 'experiments_experiments', 'ltm_ltms', ['ltm_id'], ['id'])
    # ### end Alembic commands ###