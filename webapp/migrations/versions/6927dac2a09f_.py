"""empty message

Revision ID: 6927dac2a09f
Revises: 4a27a3b3257e
Create Date: 2018-07-15 22:43:14.610606

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6927dac2a09f'
down_revision = '4a27a3b3257e'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('indexer_plugin_cache',
    sa.Column('parent_id', sa.Integer(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=False),
    sa.Column('json', sa.String(), nullable=True),
    sa.ForeignKeyConstraint(['parent_id'], ['journal_entry.id'], ondelete='cascade'),
    sa.PrimaryKeyConstraint('parent_id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('indexer_plugin_cache')
    # ### end Alembic commands ###