"""empty message

Revision ID: a987866f398b
Revises: 7d012e8b6ce6
Create Date: 2020-01-04 20:43:03.862125

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a987866f398b'
down_revision = '7d012e8b6ce6'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('bio', sa.String(length=300), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'bio')
    # ### end Alembic commands ###
