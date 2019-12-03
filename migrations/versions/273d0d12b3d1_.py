"""empty message

Revision ID: 273d0d12b3d1
Revises: 02001be7c937
Create Date: 2019-09-30 11:01:03.490043

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '273d0d12b3d1'
down_revision = '02001be7c937'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('lat', sa.Float(), nullable=True))
    op.add_column('users', sa.Column('lng', sa.Float(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'lng')
    op.drop_column('users', 'lat')
    # ### end Alembic commands ###
