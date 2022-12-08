"""empty message

Revision ID: 47c5c674cbd1
Revises: a5e927ad2dd2
Create Date: 2018-08-15 14:02:53.027768

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '47c5c674cbd1'
down_revision = 'a5e927ad2dd2'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('name_search_cache')
    op.create_index(op.f('ix_journal_entry_owner_id'), 'journal_entry', ['owner_id'], unique=False)
    op.create_index(op.f('ix_mtg_card_fetcher_cache_parent_id'), 'mtg_card_fetcher_cache', ['parent_id'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_mtg_card_fetcher_cache_parent_id'), table_name='mtg_card_fetcher_cache')
    op.drop_index(op.f('ix_journal_entry_owner_id'), table_name='journal_entry')
    op.create_table('name_search_cache',
    sa.Column('parent_id', sa.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
    sa.Column('updated_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=False),
    sa.Column('json', sa.VARCHAR(), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['parent_id'], ['journal_entry.id'], name='name_search_cache_parent_id_fkey', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('parent_id', name='name_search_cache_pkey')
    )
    # ### end Alembic commands ###