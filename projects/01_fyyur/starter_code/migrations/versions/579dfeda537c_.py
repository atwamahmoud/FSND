"""empty message

Revision ID: 579dfeda537c
Revises: 096564a61359
Create Date: 2020-08-23 01:36:55.805672

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '579dfeda537c'
down_revision = '096564a61359'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('Venue', sa.Column('seeking_talent', sa.BOOLEAN(), nullable=True))
    op.add_column('Venue', sa.Column('website', sa.String(500), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('Venue', 'seeking_talent')
    op.drop_column('Venue', 'website')
    # ### end Alembic commands ###
