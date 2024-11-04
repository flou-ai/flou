"""empty message

Revision ID: f55cc59c874c
Revises: 
Create Date: 2024-10-25 10:16:58.259632

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import flou


# revision identifiers, used by Alembic.
revision: str = 'f55cc59c874c'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('ltms',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.Column('fqn', sa.String(length=255), nullable=False),
    sa.Column('structure', flou.database.utils.JSONType(), nullable=False),
    sa.Column('kwargs', flou.database.utils.JSONType(), nullable=False),
    sa.Column('state', flou.database.utils.JSONType(), nullable=False),
    sa.Column('snapshots', flou.database.utils.JSONType(), nullable=False),
    sa.Column('playground', sa.Boolean(), nullable=False),
    sa.Column('source_id', sa.Integer(), nullable=True),
    sa.Column('rollbacks', flou.database.utils.JSONType(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.ForeignKeyConstraint(['source_id'], ['ltms.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('error',
    sa.Column('id', sa.Uuid(), nullable=False),
    sa.Column('ltm_id', sa.Integer(), nullable=False),
    sa.Column('reason', sa.String(length=30), nullable=False),
    sa.Column('item', flou.database.utils.JSONType(), nullable=False),
    sa.Column('retries', flou.database.utils.JSONType(), nullable=False),
    sa.Column('retrying', sa.Boolean(), nullable=False),
    sa.Column('success', sa.Boolean(), nullable=False),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False),
    sa.ForeignKeyConstraint(['ltm_id'], ['ltms.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('error')
    op.drop_table('ltms')
    # ### end Alembic commands ###