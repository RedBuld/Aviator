"""empty message

Revision ID: 2169059bc89d
Revises: 6bafb8b9a1a
Create Date: 2015-12-15 15:46:22.328000

"""

# revision identifiers, used by Alembic.
revision = '2169059bc89d'
down_revision = '6bafb8b9a1a'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('settings',
    sa.Column('name', sa.String(length=250), nullable=False),
    sa.Column('description', sa.String(length=250), nullable=True),
    sa.Column('value', sa.String(length=250), nullable=True),
    sa.PrimaryKeyConstraint('name'),
    sa.UniqueConstraint('name')
    )
    op.drop_table(u'settingz')
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table(u'settingz',
    sa.Column(u'name', sa.VARCHAR(length=250), nullable=False),
    sa.Column(u'description', sa.VARCHAR(length=250), nullable=True),
    sa.Column(u'value', sa.VARCHAR(length=250), nullable=True),
    sa.PrimaryKeyConstraint(u'name')
    )
    op.drop_table('settings')
    ### end Alembic commands ###
