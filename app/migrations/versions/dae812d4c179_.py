"""empty message

Revision ID: dae812d4c179
Revises: 7635c651d2a4
Create Date: 2018-10-03 12:31:34.162393

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'dae812d4c179'
down_revision = '7635c651d2a4'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('status', sa.Column('description', sa.String(length=120), nullable=True))
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('status', 'description')
    # ### end Alembic commands ###
