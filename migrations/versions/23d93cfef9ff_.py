"""empty message

Revision ID: 23d93cfef9ff
Revises: 209c9f2b0372
Create Date: 2015-12-01 17:48:13.774000

"""

# revision identifiers, used by Alembic.
revision = '23d93cfef9ff'
down_revision = '209c9f2b0372'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column('bank', sa.Integer(), nullable=True))
    op.drop_column('user', u'locale')
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('user', sa.Column(u'locale', sa.VARCHAR(length=5), nullable=True))
    op.drop_column('user', 'bank')
    ### end Alembic commands ###
