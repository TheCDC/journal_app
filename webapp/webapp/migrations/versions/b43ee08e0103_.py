"""empty message

Revision ID: b43ee08e0103
Revises: d50be64bceb7
Create Date: 2018-06-10 18:53:44.763556

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b43ee08e0103'
down_revision = 'd50be64bceb7'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index('ix_journal_entry_create_date', table_name='journal_entry')
    op.create_index(op.f('ix_journal_entry_create_date'), 'journal_entry', ['create_date'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_journal_entry_create_date'), table_name='journal_entry')
    op.create_index('ix_journal_entry_create_date', 'journal_entry', ['create_date'], unique=True)
    # ### end Alembic commands ###