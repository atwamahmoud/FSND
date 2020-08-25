"""empty message

Revision ID: 5881225d9f48
Revises: a1a967fb7b31
Create Date: 2020-08-25 03:13:43.691907

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '5881225d9f48'
down_revision = 'a1a967fb7b31'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('Show',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('vid', sa.Integer(), nullable=False),
    sa.Column('aid', sa.Integer(), nullable=False),
    sa.Column('start_time', sa.TIMESTAMP, nullable=False),
    sa.ForeignKeyConstraint(['aid'], ['Artist.id'], ),
    sa.ForeignKeyConstraint(['vid'], ['Venue.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('Show')
    # ### end Alembic commands ###
