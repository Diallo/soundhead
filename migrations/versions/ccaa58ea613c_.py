"""empty message

Revision ID: ccaa58ea613c
Revises: ec762a3d649c
Create Date: 2019-06-06 00:35:00.472440

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'ccaa58ea613c'
down_revision = 'ec762a3d649c'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('user_is_active', sa.Boolean(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('user', 'user_is_active')
    # ### end Alembic commands ###