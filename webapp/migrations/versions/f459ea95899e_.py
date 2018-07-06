"""empty message

Revision ID: f459ea95899e
Revises: d2a216551b68
Create Date: 2018-07-05 23:30:57.820046

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f459ea95899e'
down_revision = 'd2a216551b68'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_unique_constraint('_user_plugin_name', 'user_plugin_toggle', ['user_id', 'plugin_name'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint('_user_plugin_name', 'user_plugin_toggle', type_='unique')
    # ### end Alembic commands ###
