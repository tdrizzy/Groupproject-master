"""empty message

Revision ID: de2c3897b884
Revises: e400ad600354
Create Date: 2018-11-03 12:23:47.966449

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'de2c3897b884'
down_revision = 'e400ad600354'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('settings', sa.Column('maximum_team_size', sa.Integer(), nullable=True))
    op.add_column('settings', sa.Column('minimum_team_size', sa.Integer(), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('settings', 'minimum_team_size')
    op.drop_column('settings', 'maximum_team_size')
    # ### end Alembic commands ###
