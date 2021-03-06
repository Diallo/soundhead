"""empty message

Revision ID: 5829cc457eed
Revises: 
Create Date: 2019-06-12 11:47:49.574201

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5829cc457eed'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('songmoods',
    sa.Column('songid', sa.String(length=200), nullable=False),
    sa.Column('excitedness', sa.Float(), nullable=True),
    sa.Column('happiness', sa.Float(), nullable=True),
    sa.PrimaryKeyConstraint('songid')
    )
    op.create_table('songs_artists',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('songid', sa.String(length=200), nullable=True),
    sa.Column('artistid', sa.String(length=200), nullable=True),
    sa.ForeignKeyConstraint(['artistid'], ['artists.artistid'], ),
    sa.ForeignKeyConstraint(['songid'], ['songs.songid'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('songid', 'artistid', name='key')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('songs_artists')
    op.drop_table('songmoods')
    # ### end Alembic commands ###
