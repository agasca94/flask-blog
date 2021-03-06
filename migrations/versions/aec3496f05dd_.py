"""empty message

Revision ID: aec3496f05dd
Revises: a987866f398b
Create Date: 2020-01-08 15:50:19.050586

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'aec3496f05dd'
down_revision = 'a987866f398b'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('posts', sa.Column('description', sa.Text(), nullable=False))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('posts', 'description')
    # ### end Alembic commands ###
