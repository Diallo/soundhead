"""empty message

Revision ID: 6424bb3a1b5c
Revises: cd97d4a1d041
Create Date: 2019-06-18 16:10:21.731590

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '6424bb3a1b5c'
down_revision = 'cd97d4a1d041'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('songmoods', sa.Column('responses_count', sa.Integer(), nullable=True))
    op.create_foreign_key(None, 'songmoods', 'songs', ['songid'], ['songid'])
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint(None, 'songmoods', type_='foreignkey')
    op.drop_column('songmoods', 'responses_count')
    # ### end Alembic commands ###