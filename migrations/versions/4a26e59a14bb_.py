"""empty message

Revision ID: 4a26e59a14bb
Revises: 063938613373
Create Date: 2017-04-30 18:57:05.368197

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4a26e59a14bb'
down_revision = '063938613373'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('profiles', sa.Column('password', sa.String(length=255), nullable=True))
    op.drop_column('profiles', 'password_hash')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('profiles', sa.Column('password_hash', sa.VARCHAR(length=128), autoincrement=False, nullable=True))
    op.drop_column('profiles', 'password')
    # ### end Alembic commands ###
